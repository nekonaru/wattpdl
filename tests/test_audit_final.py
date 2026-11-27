"""Audit-fix regression tests: parallel probes, dry-run wording, single config write."""
import json

import pytest

from wattpdl import app as app_mod
from wattpdl import cli_args, config, library
from wattpdl.flows.common import probe_many, probe_story


class TestParallelProbes:
    def test_probe_many_preserves_order(self, monkeypatch):
        def fake(story_id, timeout=None):
            if story_id == "1":
                return ("T1", "A", [{"id": 1}, {"id": 2}], {})
            if story_id == "2":
                raise app_mod.api.StoryNotFoundError("gone")
            if story_id == "3":
                raise app_mod.api.StoryAccessError("private")

        monkeypatch.setattr(app_mod.api, "get_story_info", fake)
        results = probe_many(["1", "2", "3"], timeout=5)
        assert len(results[0][0][2]) == 2
        assert results[1][1] == "deleted"
        assert results[2][1] == "check_failed"

    def test_probe_story_never_raises(self, monkeypatch):
        def boom(story_id, timeout=None):
            raise RuntimeError("unexpected")

        monkeypatch.setattr(app_mod.api, "get_story_info", boom)
        # Only known API/network errors are classified; other errors propagate
        # so they are visible during development rather than silently hidden.
        with pytest.raises(RuntimeError):
            probe_story("1")

    def test_check_updates_json_uses_parallel_probe(self, monkeypatch, capsys, tmp_path):
        monkeypatch.setattr(library, "LIBRARY_FILE", tmp_path / "library.json")
        library.remember_story("1", "A", 1)
        library.remember_story("2", "B", 1)
        monkeypatch.setattr(app_mod.api, "get_story_info",
                            lambda story_id, timeout=None: ("T", "A", [{"id": 1}, {"id": 2}], {}))
        args = cli_args.parse_args(["--check-updates", "--json"])
        from wattpdl.flows.library import run_check_updates

        run_check_updates(args)
        rows = json.loads(capsys.readouterr().out)
        assert [r["id"] for r in rows] == ["1", "2"]
        assert all(r["status"] == "new_chapters" for r in rows)


class TestDryRunTally:
    def test_user_dry_run_says_simulation(self, monkeypatch, capsys, tmp_path):
        monkeypatch.setattr(app_mod.api, "get_author_stories", lambda *a, **kw: [
            {"id": "11", "title": "A", "num_parts": 1, "completed": True},
        ])
        monkeypatch.setattr(app_mod.api, "get_story_info",
                            lambda story_id, timeout=None: ("A", "P", [{"id": 1}], {}))
        monkeypatch.setattr(app_mod, "run_download", lambda *a, **kw: None)
        monkeypatch.setattr(app_mod.config_mod, "CONFIG_FILE", tmp_path / "config.json")
        args = cli_args.parse_args(["--user", "someone", "--dry-run"])
        from wattpdl.flows.batch import run_user_mode

        run_user_mode(args)
        assert "Simulation" in capsys.readouterr().out


class TestSinglePreferenceWrite:
    def test_batch_flow_saves_config_once(self, monkeypatch, tmp_path):
        monkeypatch.setattr(app_mod.api, "get_author_stories", lambda *a, **kw: [
            {"id": "11", "title": "A", "num_parts": 1, "completed": True},
            {"id": "12", "title": "B", "num_parts": 2, "completed": True},
        ])
        monkeypatch.setattr(app_mod.api, "get_story_info",
                            lambda story_id, timeout=None: ("A", "P", [{"id": 1}], {}))
        monkeypatch.setattr(app_mod, "run_download", lambda *a, **kw: None)
        calls = []
        monkeypatch.setattr(app_mod.config_mod, "save_config", lambda **kw: calls.append(kw))
        args = cli_args.parse_args(["--user", "someone"])
        from wattpdl.flows.batch import run_user_mode

        run_user_mode(args)
        assert len(calls) == 1
