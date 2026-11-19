"""
Security-style regression tests for the audit batch:
- safe_filename must cap by UTF-8 bytes (255-byte Linux filename limit)
- saved config with an unknown file_format must fall back to the default
- a failing progress flush must not fail the chapter
"""
import json

from wattpdl.writers import safe_filename


class TestSafeFilenameBytes:
    def test_cjk_title_is_byte_capped(self):
        name = safe_filename("章" * 300)
        assert len(name.encode("utf-8")) <= 100

    def test_ascii_title_still_capped_at_100_chars(self):
        assert len(safe_filename("A" * 500)) <= 100

    def test_empty_and_symbolic_names_still_fall_back(self):
        assert safe_filename("") == "wattpad_story"
        assert safe_filename("...") == "wattpad_story"


class TestConfigFormatFallback:
    def test_unknown_saved_format_falls_back_to_txt(self, tmp_path, monkeypatch):
        monkeypatch.setattr("wattpdl.config.CONFIG_FILE", tmp_path / "config.json")
        (tmp_path / "config.json").write_text(json.dumps({"file_format": "9"}), encoding="utf-8")
        from wattpdl import config

        assert config.load_config()["file_format"] == "1"

    def test_valid_saved_format_is_kept(self, tmp_path, monkeypatch):
        monkeypatch.setattr("wattpdl.config.CONFIG_FILE", tmp_path / "config.json")
        (tmp_path / "config.json").write_text(json.dumps({"file_format": "5"}), encoding="utf-8")
        from wattpdl import config

        assert config.load_config()["file_format"] == "5"


class TestProgressWriteNeverFailsChapter:
    def test_progress_store_survives_unwritable_dir(self, tmp_path, monkeypatch):
        blocker = tmp_path / "blocker"
        blocker.write_text("file, not a directory", encoding="utf-8")
        monkeypatch.setattr("wattpdl.progress.PROGRESS_DIR", blocker)
        from wattpdl.progress import ProgressStore

        store = ProgressStore("99")
        store.mark_done(1, "Bab 1", "isi bab")  # must not raise
        assert store.has(1) is True

    def test_save_chapter_progress_survives_unwritable_dir(self, tmp_path, monkeypatch):
        blocker = tmp_path / "blocker"
        blocker.write_text("file, not a directory", encoding="utf-8")
        monkeypatch.setattr("wattpdl.progress.PROGRESS_DIR", blocker)
        from wattpdl.progress import save_chapter_progress

        save_chapter_progress("99", 1, "Bab 1", "isi bab")  # must not raise
