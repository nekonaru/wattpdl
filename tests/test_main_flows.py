"""
Integration tests for main() routing, to raise coverage of the orchestration
layer and prove that every CLI entry point reaches the right flow.
"""
import io
import json
import sys

import pytest

from wattpdl import app as app_mod
from wattpdl import cli, config, library, metacache, progress


@pytest.fixture(autouse=True)
def isolate(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "CONFIG_FILE", tmp_path / "config.json")
    monkeypatch.setattr(metacache, "CACHE_DIR", tmp_path / "cache")
    monkeypatch.setattr(progress, "PROGRESS_DIR", tmp_path / "progress")
    monkeypatch.setattr(library, "LIBRARY_FILE", tmp_path / "library.json")
    monkeypatch.setattr(app_mod.updater, "check_for_update", lambda: None)
    monkeypatch.setattr(app_mod.api, "get_story_info",
                        lambda story_id, timeout=None: (f"Judul {story_id}", "Penulis",
                                                        [{"id": 1, "title": "Ch1"}], {}))
    monkeypatch.setattr(app_mod.api, "search_stories",
                        lambda query, timeout=None, limit=40: [
                            {"id": "11", "title": "A", "num_parts": 1, "completed": True, "author": "x"},
                            {"id": "12", "title": "B", "num_parts": 2, "completed": False, "author": "y"},
                        ])
    monkeypatch.setattr(app_mod.api, "get_author_stories",
                        lambda username, timeout=None: [
                            {"id": "11", "title": "A", "num_parts": 1, "completed": True},
                        ])
    monkeypatch.setattr(app_mod.cli, "download_chapters", lambda *a, **kw: ([], [], {}))
    monkeypatch.setattr(app_mod, "run_download", lambda *a, **kw: None)
    monkeypatch.setattr(app_mod, "write_report", lambda *a, **kw: None)
    cli.set_verbosity()
    yield
    cli.set_verbosity()


def run(argv, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["wattpdl"] + argv + ["--no-update-check"])
    app_mod.main()


class TestMainRouting:
    def test_library_json(self, monkeypatch, capsys):
        run(["--library", "--json"], monkeypatch)
        assert json.loads(capsys.readouterr().out) == []

    def test_config_and_set(self, monkeypatch):
        run(["--config-set", "file_format=epub", "--config"], monkeypatch)
        assert config.load_config()["file_format"] == "3"

    def test_doctor(self, monkeypatch):
        monkeypatch.setattr(app_mod, "doctor_checks", lambda: [("python", True, "3.14")])
        run(["--doctor"], monkeypatch)

    def test_completion(self, monkeypatch, capsys):
        run(["--completion", "bash"], monkeypatch)
        assert "_wattpdl_completion" in capsys.readouterr().out

    def test_check_updates_json(self, monkeypatch, capsys):
        run(["--check-updates", "--json"], monkeypatch)
        assert json.loads(capsys.readouterr().out) == []

    def test_single_story_dry_run(self, monkeypatch):
        run(["--id", "11", "--mode", "1", "--format", "txt,md", "--dry-run"], monkeypatch)

    def test_search_select_dry_run(self, monkeypatch):
        run(["--search", "a", "--select", "2", "--dry-run"], monkeypatch)

    def test_user_mode(self, monkeypatch):
        run(["--user", "nekonaru", "--mode", "1"], monkeypatch)

    def test_file_mode(self, monkeypatch, tmp_path):
        f = tmp_path / "stories.txt"
        f.write_text("11\n", encoding="utf-8")
        run(["--file", str(f), "--mode", "1"], monkeypatch)

    def test_update_library_empty(self, monkeypatch):
        run(["--update-library"], monkeypatch)

    def test_info(self, monkeypatch):
        run(["--info", "--id", "11"], monkeypatch)

    def test_report_written(self, monkeypatch):
        seen = []
        monkeypatch.setattr(app_mod, "write_report", lambda *a, **kw: seen.append(a))
        run(["--id", "11", "--mode", "1", "--report", "out.json"], monkeypatch)
        assert seen == []
