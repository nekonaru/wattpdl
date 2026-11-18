"""
Security regression tests ("try to break it") for the protections added
during the security review of wattpdl. Kept in the normal test suite so CI
runs them on every push.
"""
import json
import pathlib

import pytest

from wattpdl import api as api_mod
from wattpdl import cli_args, library, metacache, progress, updater
from wattpdl.writers import safe_filename

SRC_ROOT = pathlib.Path(__file__).resolve().parent.parent / "src"

FORBIDDEN_CALLS = [
    b"os.system",
    b"os.popen",
    b"shell=True",
    b"subprocess",
    b"pickle",
    b"yaml.load",
    b"verify=False",
    b"eval(",
    b"exec(",
]


class TestSourceScan:
    def test_no_dangerous_calls_in_source(self):
        offenders = []
        for py in SRC_ROOT.rglob("*.py"):
            data = py.read_bytes()
            for token in FORBIDDEN_CALLS:
                if token in data:
                    offenders.append((py.name, token.decode()))
        assert offenders == []


class TestSafeFilename:
    def test_path_traversal_is_removed(self):
        name = safe_filename("../../etc/passwd")
        assert "/" not in name
        assert "\\" not in name
        assert ".." not in name

    def test_windows_traversal_is_removed(self):
        name = safe_filename("..\\..\\windows\\system32\\config")
        assert "/" not in name
        assert "\\" not in name
        assert ".." not in name

    def test_windows_reserved_names_are_prefixed(self):
        assert safe_filename("CON") == "_CON"
        assert safe_filename("aux") == "_aux"

    def test_empty_and_symbolic_names_fall_back(self):
        assert safe_filename("") == "wattpad_story"
        assert safe_filename("...") == "wattpad_story"

    def test_very_long_title_is_truncated(self):
        assert len(safe_filename("A" * 500)) <= 100


class TestCorruptCacheFiles:
    def test_metacache_garbage_returns_none(self, tmp_path, monkeypatch):
        monkeypatch.setattr(metacache, "CACHE_DIR", tmp_path)
        (tmp_path / "1.json").write_text("{" + "[" * 10000, encoding="utf-8")
        assert metacache.get_cached_story("1") is None

    def test_metacache_deep_nesting_returns_none(self, tmp_path, monkeypatch):
        monkeypatch.setattr(metacache, "CACHE_DIR", tmp_path)
        (tmp_path / "1.json").write_text("[" * 5000 + "]" * 5000, encoding="utf-8")
        assert metacache.get_cached_story("1") is None

    def test_progress_garbage_returns_empty(self, tmp_path, monkeypatch):
        monkeypatch.setattr(progress, "PROGRESS_DIR", tmp_path)
        (tmp_path / "1.json").write_text("not json at all [[", encoding="utf-8")
        assert progress.load_progress("1") == {}

    def test_progress_store_garbage_returns_empty(self, tmp_path, monkeypatch):
        monkeypatch.setattr(progress, "PROGRESS_DIR", tmp_path)
        (tmp_path / "1.json").write_text("{" * 300, encoding="utf-8")
        store = progress.ProgressStore("1")
        assert store.has(1) is False

    def test_library_garbage_returns_empty(self, tmp_path, monkeypatch):
        monkeypatch.setattr(library, "LIBRARY_FILE", tmp_path / "library.json")
        (tmp_path / "library.json").write_text("{[broken", encoding="utf-8")
        assert library.load_library() == {}

    def test_updater_cache_garbage_returns_empty(self, tmp_path, monkeypatch):
        monkeypatch.setattr(updater, "CACHE_FILE", tmp_path / "update_check.json")
        (tmp_path / "update_check.json").write_text("{not json", encoding="utf-8")
        assert updater._load_cache() == {}

    def test_config_garbage_returns_defaults(self, tmp_path, monkeypatch):
        monkeypatch.setattr("wattpdl.config.CONFIG_FILE", tmp_path / "config.json")
        (tmp_path / "config.json").write_text("{invalid", encoding="utf-8")
        from wattpdl import config

        assert config.load_config() == config.DEFAULT_CONFIG


class TestNoPrivateNetworkAccess:
    LOOPBACK = "127.0.0.1"
    RFC1918 = "192.168.1.1"
    CLOUD_METADATA = "169.254.169.254"
    CGNAT = "100.64.0.1"

    @pytest.mark.parametrize("host", ["127.0.0.1", "192.168.1.1", "10.0.0.4", "172.16.0.9",
                                      "169.254.169.254", "100.64.0.1"])
    def test_private_hosts_are_rejected(self, host, monkeypatch):
        def fake_getaddrinfo(name, port, *a, **kw):
            return [(2, 1, 6, "", (host, 0))]

        monkeypatch.setattr("socket.getaddrinfo", fake_getaddrinfo)
        assert api_mod._is_private_host(host) is True

    @pytest.mark.parametrize("host", ["localhost", "foo.localhost"])
    def test_localhost_is_rejected(self, host):
        assert api_mod._is_private_host(host) is True

    def test_download_image_never_reaches_private_hosts(self, monkeypatch):
        calls = []
        monkeypatch.setattr("socket.getaddrinfo",
                            lambda name, port, *a, **kw: [(2, 1, 6, "", ("10.1.2.3", 0))])
        monkeypatch.setattr(api_mod, "_http_session",
                            lambda: calls.append("session-created") or type("S", (), {})())
        assert api_mod.download_image("http://internal.local/secret.jpg") is None
        assert calls == []

    def test_download_image_size_cap(self, monkeypatch):
        monkeypatch.setattr(api_mod, "_is_private_host", lambda host: False)
        big_chunk = b"x" * 65536
        chunks = [big_chunk] * (api_mod.MAX_IMAGE_BYTES // 65536 + 2)

        class FakeResp:
            status_code = 200

            def raise_for_status(self):
                return None

            def iter_content(self, chunk_size=65536):
                yield from chunks

        class FakeSession:
            def get(self, url, timeout=None, **kw):
                return FakeResp()

        monkeypatch.setattr(api_mod, "_http_session", lambda: FakeSession())
        assert api_mod.download_image("https://example.com/huge.jpg") is None


class TestCliBoundaryValidation:
    def test_username_rejects_traversal(self):
        args = cli_args.parse_args(["--user", "../../evil"])
        with pytest.raises(ValueError):
            cli_args.validate_common_args(args)

    def test_username_rejects_spaces(self):
        args = cli_args.parse_args(["--user", "bad name"])
        with pytest.raises(ValueError):
            cli_args.validate_common_args(args)

    def test_username_rejects_too_long(self):
        args = cli_args.parse_args(["--user", "a" * 33])
        with pytest.raises(ValueError):
            cli_args.validate_common_args(args)

    def test_username_accepts_valid_names(self):
        args = cli_args.parse_args(["--user", "nekonaru-1_2"])
        cli_args.validate_common_args(args)

    def test_watch_interval_zero_rejected(self):
        args = cli_args.parse_args(["--id", "1", "--mode", "1", "--watch-interval", "0"])
        with pytest.raises(ValueError):
            cli_args.validate_common_args(args)

    def test_story_id_must_be_digits(self):
        with pytest.raises(ValueError):
            api_mod.extract_story_id("notavalidid!!")

    def test_chapter_link_is_rejected_with_specific_message(self):
        with pytest.raises(ValueError):
            api_mod.extract_story_id("https://www.wattpad.com/1234567-some-title-part")


class TestSecurityHelpers:
    def test_host_resolution_failure_is_not_blocked(self, monkeypatch):
        def boom(name, port, *a, **kw):
            raise OSError("offline")

        monkeypatch.setattr("socket.getaddrinfo", boom)
        # DNS failure is allowed through; the request itself will fail anyway.
        assert api_mod._is_private_host("no-such-host-wattpdl.example") is False
