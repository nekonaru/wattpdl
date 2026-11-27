"""
Wave 1 regression tests: multi-format, reports, config commands,
doctor, completion, verbosity, atomic writes.
"""
import json

import pytest

from wattpdl import app as app_mod
from wattpdl import cli, cli_args


class TestMultiFormat:
    def test_parse_formats_single_list_all(self):
        assert cli_args.parse_formats("epub") == ["epub"]
        assert cli_args.parse_formats("txt,epub,txt") == ["txt", "epub"]
        assert cli_args.parse_formats("all") == ["txt", "docx", "epub", "md", "pdf"]
        assert cli_args.parse_formats(None) == []

    def test_parse_formats_rejects_unknown(self):
        with pytest.raises(ValueError):
            cli_args.parse_formats("txt,docm")

    def test_resolve_codes_uses_saved_default(self):
        assert cli_args.resolve_codes(None, "3") == ["3"]
        assert cli_args.resolve_codes("txt,epub", "1") == ["1", "3"]

    def test_output_paths_are_distinct_per_format(self, tmp_path):
        parts = [(1, {"id": 1, "title": "Ch1"})]
        paths = [app_mod._output_path(tmp_path, "Story", "1", code, parts) for code in ("1", "3")]
        assert [p.name for p in paths] == ["Story.txt", "Story.epub"]
        zips = [app_mod._output_path(tmp_path, "Story", "2", code, parts) for code in ("1", "3")]
        assert [p.name for p in zips] == ["Story.zip", "Story_epub.zip"]


class TestReports:
    def test_json_report(self, tmp_path):
        entries = [{"story_id": "1", "title": "Story", "files": ["a.txt"]}]
        path = tmp_path / "report.json"
        app_mod.write_report(path, entries)
        assert json.loads(path.read_text(encoding="utf-8"))[0]["story_id"] == "1"

    def test_csv_report(self, tmp_path):
        entries = [{"story_id": "1", "title": "Story", "formats": ["txt", "md"], "files": ["a.txt", "a.md"]}]
        path = tmp_path / "report.csv"
        app_mod.write_report(path, entries)
        text = path.read_text(encoding="utf-8")
        assert "story_id" in text
        assert "a.txt|a.md" in text


class TestConfigCommands:
    def test_parse_config_set(self):
        updates = cli_args.parse_config_set(["file_format=epub", "ui_lang=id"])
        assert updates == {"file_format": "3", "ui_lang": "id"}

    def test_parse_config_set_rejects_unknown_key(self):
        with pytest.raises(ValueError):
            cli_args.parse_config_set(["nope=1"])

    def test_config_commands_apply(self, tmp_path, monkeypatch):
        monkeypatch.setattr("wattpdl.config.CONFIG_FILE", tmp_path / "config.json")
        args = cli_args.parse_args(["--config-set", "file_format=pdf"])
        app_mod.run_config_commands(args)
        from wattpdl import config

        assert config.load_config()["file_format"] == "5"


class TestDoctor:
    def test_doctor_checks_report_rows(self, monkeypatch):
        monkeypatch.setattr(app_mod.api, "get_story_info",
                            lambda *a, **kw: ("T", "A", [{"id": 1}], {}))
        rows = app_mod.doctor_checks()
        names = [row[0] for row in rows]
        assert len(rows) >= 5
        assert all(isinstance(row[1], bool) for row in rows)
        assert names[0]  # non-empty labels


class TestCompletion:
    @pytest.mark.parametrize("shell", ["bash", "zsh", "fish", "powershell"])
    def test_script_lists_flags(self, shell):
        script = app_mod.completion_script(shell)
        assert "wattpdl" in script
        if shell == "fish":
            assert "-l search" in script
            assert "-l format" in script
        else:
            assert "--search" in script
            assert "--format" in script


class TestVerbosity:
    def test_quiet_sets_console(self):
        cli.set_verbosity(quiet=True, verbose=True)
        assert cli.console.quiet is True
        assert cli.VERBOSE is True
        cli.set_verbosity()  # restore for other tests
        assert cli.console.quiet is False
        assert cli.VERBOSE is False


class TestAtomicOutput:
    def test_failed_replace_leaves_no_target(self, tmp_path, monkeypatch):
        target = tmp_path / "story.txt"
        monkeypatch.setattr("os.replace", lambda *a, **kw: (_ for _ in ()).throw(OSError("disk full")))
        with pytest.raises(OSError):
            with app_mod.writers._atomic_output(target) as tmp:
                tmp.write_text("partial", encoding="utf-8")
        assert not target.exists()
        assert list(tmp_path.glob(".wattpdl-*")) == []


class TestRealMultiFormatWrites:
    """One download, several output files (no network, real writers)."""

    @pytest.fixture(autouse=True)
    def isolate(self, tmp_path, monkeypatch):
        from wattpdl import cli as cli_mod
        from wattpdl import config as config_mod
        from wattpdl import progress as progress_mod

        self.calls = []

        def fake_download(*a, **kw):
            self.calls.append(a)
            return [(1, "Bab 1", "Isi bab satu.")], [], {}

        monkeypatch.setattr(cli_mod, "download_chapters", fake_download)
        monkeypatch.setattr(progress_mod, "PROGRESS_DIR", tmp_path / "progress")
        monkeypatch.setattr(config_mod, "CONFIG_FILE", tmp_path / "config.json")
        app_mod.REPORT_ENTRIES.clear()

    def test_two_formats_written_once(self, tmp_path):
        app_mod.run_download("11", "Judul Cerita", "Penulis",
                             [{"id": 1, "title": "Bab 1"}], "1", "1", tmp_path,
                             formats=["1", "3"], timeout=5)
        assert (tmp_path / "Judul_Cerita.txt").exists()
        assert (tmp_path / "Judul_Cerita.epub").exists()
        assert len(self.calls) == 1
        assert len(app_mod.REPORT_ENTRIES) == 1
        assert set(app_mod.REPORT_ENTRIES[0]["formats"]) == {"txt", "epub"}

    def test_docx_and_md(self, tmp_path):
        app_mod.run_download("12", "Buku Dua", "Penulis",
                             [{"id": 1, "title": "Bab 1"}], "1", "1", tmp_path,
                             formats=["2", "4"], timeout=5)
        assert (tmp_path / "Buku_Dua.docx").exists()
        assert (tmp_path / "Buku_Dua.md").exists()

    def test_pdf(self, tmp_path):
        app_mod.run_download("13", "Buku Tiga", "Penulis",
                             [{"id": 1, "title": "Bab 1"}], "1", "1", tmp_path,
                             formats=["5"], timeout=5)
        assert (tmp_path / "Buku_Tiga.pdf").read_bytes().startswith(b"%PDF")

    def test_separate_zip_two_formats(self, tmp_path):
        app_mod.run_download("14", "Buku Empat", "Penulis",
                             [{"id": 1, "title": "Bab 1"}], "2", "1", tmp_path,
                             formats=["1", "3"], timeout=5)
        assert (tmp_path / "Buku_Empat.zip").exists()
        assert (tmp_path / "Buku_Empat_epub.zip").exists()


class TestInteractiveFlowCoverage:
    def test_interactive_single_chapter(self, monkeypatch, tmp_path):
        from wattpdl import metacache as meta_mod
        from wattpdl import progress as progress_mod

        monkeypatch.setattr(meta_mod, "CACHE_DIR", tmp_path / "cache")
        monkeypatch.setattr(progress_mod, "PROGRESS_DIR", tmp_path / "progress")
        monkeypatch.setattr(app_mod.api, "get_story_info",
                            lambda story_id, timeout=None: ("Judul", "Penulis", [{"id": 1, "title": "Ch1"}], {}))
        answers = iter(["11", "1", "1", ""])
        monkeypatch.setattr(app_mod.cli.Prompt, "ask", lambda *a, **kw: next(answers))
        calls = []
        monkeypatch.setattr(app_mod, "run_download", lambda *a, **kw: calls.append((a, kw)))
        args = cli_args.parse_args([])
        app_mod.run_interactive(args)
        assert len(calls) == 1
        assert calls[0][1]["interactive"] is True

    def test_interactive_with_parallel_and_images(self, monkeypatch, tmp_path):
        from wattpdl import metacache as meta_mod

        monkeypatch.setattr(meta_mod, "CACHE_DIR", tmp_path / "cache")
        monkeypatch.setattr(app_mod.api, "get_story_info",
                            lambda story_id, timeout=None: ("Judul", "Penulis",
                                                            [{"id": i, "title": f"Ch{i}"} for i in range(5)], {}))
        answers = iter(["11", "1", "3", ""])
        confirms = iter([True, True])  # include images, parallel
        monkeypatch.setattr(app_mod.cli.Prompt, "ask", lambda *a, **kw: next(answers))
        monkeypatch.setattr(app_mod.cli.Confirm, "ask", lambda *a, **kw: next(confirms))
        monkeypatch.setattr(app_mod.cli.IntPrompt, "ask", lambda *a, **kw: 3)
        calls = []
        monkeypatch.setattr(app_mod, "run_download", lambda *a, **kw: calls.append((a, kw)))
        args = cli_args.parse_args([])
        app_mod.run_interactive(args)
        assert len(calls) == 1
        assert calls[0][1]["include_images"] is True
        assert calls[0][1]["workers"] == 3
