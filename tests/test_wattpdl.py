"""
Unit test untuk fungsi-fungsi murni (pure function) di package wattpdl.
Jalankan dengan: pytest
(path ke src/ sudah diatur lewat [tool.pytest.ini_options] di pyproject.toml)
"""
import pathlib
import tempfile

import pytest
import requests

from wattpdl import app as app_mod
from wattpdl import cli as cli_mod
from wattpdl import cli_args
from wattpdl import config as config_mod
from wattpdl import progress as progress_mod
from wattpdl.api import extract_story_id, get_chapter_html
from wattpdl.cli import format_duration, parse_chapter_selection
from wattpdl.writers import html_to_text, safe_filename, write_combined_epub, write_separate_epub_zip


class TestExtractStoryId:
    def test_full_url(self):
        url = "https://www.wattpad.com/story/398440633-judul-cerita"
        assert extract_story_id(url) == "398440633"

    def test_bare_id(self):
        assert extract_story_id("398440633") == "398440633"

    def test_id_with_whitespace(self):
        assert extract_story_id("  398440633  ") == "398440633"

    def test_invalid_input_raises(self):
        with pytest.raises(ValueError):
            extract_story_id("bukan-link-atau-id")

    def test_empty_input_raises(self):
        with pytest.raises(ValueError):
            extract_story_id("")

    def test_chapter_link_raises_specific_message(self):
        # URL per-chapter (format mobile/share, tanpa "story/") harus dikenali
        # dan dikasih pesan yang jelas, bukan pesan generik "tidak dikenali".
        with pytest.raises(ValueError, match="chapter"):
            extract_story_id("https://www.wattpad.com/1234567-judul-part")


class TestSafeFilename:
    def test_removes_illegal_characters(self):
        assert safe_filename('judul: cerita/aneh?*"') == "judul_ceritaaneh"

    def test_spaces_become_underscore(self):
        assert safe_filename("Judul Cerita Keren") == "Judul_Cerita_Keren"

    def test_empty_input_has_fallback(self):
        assert safe_filename("") == "cerita_wattpad"

    def test_only_illegal_chars_has_fallback(self):
        assert safe_filename('///???***') == "cerita_wattpad"

    def test_preserves_unicode_letters(self):
        # Judul berbahasa Indonesia dengan huruf biasa harus tetap utuh
        assert safe_filename("Cerita Cinta Sederhana") == "Cerita_Cinta_Sederhana"


class TestParseChapterSelection:
    def test_single_numbers(self):
        assert parse_chapter_selection("1,3,5", total=10) == [1, 3, 5]

    def test_range(self):
        assert parse_chapter_selection("5-8", total=10) == [5, 6, 7, 8]

    def test_mixed(self):
        assert parse_chapter_selection("1,3,5-8", total=10) == [1, 3, 5, 6, 7, 8]

    def test_reversed_range_is_normalized(self):
        assert parse_chapter_selection("8-5", total=10) == [5, 6, 7, 8]

    def test_duplicates_are_deduped(self):
        assert parse_chapter_selection("1,1,2,2", total=10) == [1, 2]

    def test_out_of_range_numbers_are_ignored(self):
        assert parse_chapter_selection("1,50", total=10) == [1]

    def test_empty_input_raises(self):
        with pytest.raises(ValueError):
            parse_chapter_selection("", total=10)

    def test_non_numeric_raises(self):
        with pytest.raises(ValueError):
            parse_chapter_selection("abc", total=10)

    def test_invalid_range_raises(self):
        with pytest.raises(ValueError):
            parse_chapter_selection("1-abc", total=10)

    def test_all_out_of_range_raises(self):
        with pytest.raises(ValueError):
            parse_chapter_selection("50,60", total=10)


class TestHtmlToText:
    def test_strips_paragraph_tags(self):
        assert html_to_text("<p>Halo</p><p>Dunia</p>") == "Halo\n\nDunia"

    def test_converts_br_to_newline(self):
        assert html_to_text("Baris satu<br>Baris dua") == "Baris satu\nBaris dua"

    def test_strips_unknown_tags(self):
        assert html_to_text("<span>Halo</span>") == "Halo"

    def test_unescapes_html_entities(self):
        assert html_to_text("Tom &amp; Jerry &quot;kejar&quot;") == 'Tom & Jerry "kejar"'

    def test_apostrophe_entity(self):
        assert html_to_text("Aku&#39;s book") == "Aku's book"

    def test_collapses_excess_blank_lines(self):
        result = html_to_text("<p>A</p><p></p><p></p><p>B</p>")
        assert "\n\n\n" not in result


class TestFormatDuration:
    def test_seconds_only(self):
        assert format_duration(45) == "45d"

    def test_minutes_and_seconds(self):
        assert format_duration(138) == "2m 18d"

    def test_zero(self):
        assert format_duration(0) == "0d"


class TestConfig:
    @pytest.fixture(autouse=True)
    def isolate_config(self, tmp_path, monkeypatch):
        # Jangan pernah baca/tulis ke config asli user saat testing
        monkeypatch.setattr(config_mod, "CONFIG_DIR", tmp_path / ".wattpdl")
        monkeypatch.setattr(config_mod, "CONFIG_FILE", tmp_path / ".wattpdl" / "config.json")

    def test_load_config_returns_default_when_missing(self):
        cfg = config_mod.load_config()
        assert cfg == config_mod.DEFAULT_CONFIG

    def test_save_and_load_roundtrip(self):
        config_mod.save_config(save_dir="/tmp/downloads", file_format="2")
        cfg = config_mod.load_config()
        assert cfg["save_dir"] == "/tmp/downloads"
        assert cfg["file_format"] == "2"

    def test_save_config_merges_not_replaces(self):
        config_mod.save_config(save_dir="/tmp/downloads")
        config_mod.save_config(file_format="2")
        cfg = config_mod.load_config()
        assert cfg["save_dir"] == "/tmp/downloads"
        assert cfg["file_format"] == "2"

    def test_load_config_survives_corrupt_file(self):
        config_mod.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        config_mod.CONFIG_FILE.write_text("bukan json valid {{{", encoding="utf-8")
        cfg = config_mod.load_config()
        assert cfg == config_mod.DEFAULT_CONFIG

    def test_unknown_keys_are_ignored(self):
        config_mod.save_config(save_dir="/tmp/x", key_aneh="harusnya_diabaikan")
        cfg = config_mod.load_config()
        assert "key_aneh" not in cfg


class TestProgress:
    @pytest.fixture(autouse=True)
    def isolate_progress(self, tmp_path, monkeypatch):
        monkeypatch.setattr(progress_mod, "PROGRESS_DIR", tmp_path / "progress")

    def test_load_progress_empty_when_missing(self):
        assert progress_mod.load_progress("12345") == {}

    def test_save_and_load_chapter(self):
        progress_mod.save_chapter_progress("12345", 111, "Chapter 1", "Halo dunia")
        data = progress_mod.load_progress("12345")
        assert data["111"]["title"] == "Chapter 1"
        assert data["111"]["text"] == "Halo dunia"

    def test_multiple_chapters_accumulate(self):
        progress_mod.save_chapter_progress("12345", 111, "Ch 1", "Teks 1")
        progress_mod.save_chapter_progress("12345", 222, "Ch 2", "Teks 2")
        data = progress_mod.load_progress("12345")
        assert set(data.keys()) == {"111", "222"}

    def test_different_stories_are_isolated(self):
        progress_mod.save_chapter_progress("story-a", 1, "Ch 1", "A")
        progress_mod.save_chapter_progress("story-b", 1, "Ch 1", "B")
        assert progress_mod.load_progress("story-a")["1"]["text"] == "A"
        assert progress_mod.load_progress("story-b")["1"]["text"] == "B"

    def test_clear_progress_removes_file(self):
        progress_mod.save_chapter_progress("12345", 111, "Ch 1", "Teks")
        progress_mod.clear_progress("12345")
        assert progress_mod.load_progress("12345") == {}

    def test_clear_progress_on_nonexistent_is_safe(self):
        progress_mod.clear_progress("tidak-pernah-ada")  # tidak boleh raise


class TestCliArgs:
    def test_default_is_interactive_mode(self):
        args = cli_args.parse_args([])
        assert args.id is None

    def test_parses_non_interactive_args(self):
        args = cli_args.parse_args([
            "--id", "398440633", "--mode", "1", "--format", "docx",
            "--output-dir", "/tmp/out",
        ])
        assert args.id == "398440633"
        assert args.mode == "1"
        assert args.format == "docx"
        assert args.output_dir == "/tmp/out"

    def test_parses_chapters_for_mode_3(self):
        args = cli_args.parse_args(["--id", "1", "--mode", "3", "--chapters", "1,3,5-8"])
        assert args.chapters == "1,3,5-8"

    def test_parses_chapter_for_mode_4(self):
        args = cli_args.parse_args(["--id", "1", "--mode", "4", "--chapter", "5"])
        assert args.chapter == 5

    def test_invalid_mode_rejected(self):
        with pytest.raises(SystemExit):
            cli_args.parse_args(["--id", "1", "--mode", "9"])

    def test_invalid_format_rejected(self):
        with pytest.raises(SystemExit):
            cli_args.parse_args(["--id", "1", "--format", "pdf"])

    def test_validate_requires_mode(self):
        args = cli_args.parse_args(["--id", "1"])
        with pytest.raises(ValueError):
            cli_args.validate_non_interactive_args(args)

    def test_validate_requires_chapters_for_mode_3(self):
        args = cli_args.parse_args(["--id", "1", "--mode", "3"])
        with pytest.raises(ValueError):
            cli_args.validate_non_interactive_args(args)

    def test_validate_requires_chapter_for_mode_4(self):
        args = cli_args.parse_args(["--id", "1", "--mode", "4"])
        with pytest.raises(ValueError):
            cli_args.validate_non_interactive_args(args)

    def test_validate_passes_for_mode_1(self):
        args = cli_args.parse_args(["--id", "1", "--mode", "1"])
        cli_args.validate_non_interactive_args(args)  # tidak boleh raise

    def test_format_to_code_mapping(self):
        assert cli_args.FORMAT_TO_CODE == {"txt": "1", "docx": "2", "epub": "3"}


class TestEpubWriters:
    @pytest.fixture
    def sample_results(self):
        return [
            (1, "Chapter 1: Awal", "Paragraf pertama.\nBaris kedua.\n\nParagraf kedua."),
            (2, "Chapter 2: Tengah", "Cerita berlanjut & makin seru."),
        ]

    def test_combined_epub_is_readable(self, tmp_path, sample_results):
        from ebooklib import epub

        out = tmp_path / "cerita.epub"
        write_combined_epub(out, "Judul Cerita", "Penulis X", "12345", sample_results)

        assert out.exists()
        assert out.stat().st_size > 0

        book = epub.read_epub(str(out))
        titles = dict(book.get_metadata("DC", "title"))
        assert "Judul Cerita" in titles

    def test_combined_epub_contains_all_chapters(self, tmp_path, sample_results):
        from ebooklib import epub

        out = tmp_path / "cerita.epub"
        write_combined_epub(out, "Judul", "Penulis", "1", sample_results)

        book = epub.read_epub(str(out))
        doc_names = [item.get_name() for item in book.get_items() if item.get_type() == 9]
        assert "chap_001.xhtml" in doc_names
        assert "chap_002.xhtml" in doc_names

    def test_separate_epub_zip_creates_valid_zip(self, tmp_path, sample_results):
        import zipfile

        out = tmp_path / "cerita_terpisah.zip"
        write_separate_epub_zip(out, "Judul", "Penulis", "1", sample_results)

        assert out.exists()
        with zipfile.ZipFile(out) as zf:
            names = zf.namelist()
            assert any(n.endswith("_Chapter_1_Awal.epub") for n in names)
            assert any(n.endswith("_Chapter_2_Tengah.epub") for n in names)
            assert "000_info.epub" in names

    def test_separate_epub_zip_has_unique_identifiers(self, tmp_path, sample_results):
        # Bug 2: identifier EPUB dulu identik untuk semua file per-chapter.
        # Sekarang harus unik per file (termasuk file info).
        import zipfile

        from ebooklib import epub

        out = tmp_path / "cerita_terpisah.zip"
        write_separate_epub_zip(out, "Judul", "Penulis", "999", sample_results)

        identifiers = []
        with zipfile.ZipFile(out) as zf:
            for name in zf.namelist():
                extracted = tmp_path / name
                extracted.write_bytes(zf.read(name))
                book = epub.read_epub(str(extracted))
                identifiers.append(book.get_metadata("DC", "identifier")[0][0])

        assert len(identifiers) == len(set(identifiers)), f"Identifier tidak unik: {identifiers}"


class TestGetChapterHtml:
    def test_retries_zero_raises_value_error(self):
        # Bug 3: sebelumnya retries=0 diam-diam mengembalikan string kosong.
        with pytest.raises(ValueError, match="retries"):
            get_chapter_html(123, retries=0)

    def test_negative_retries_raises_value_error(self):
        with pytest.raises(ValueError, match="retries"):
            get_chapter_html(123, retries=-1)


class TestFetchStoryOrExit:
    def test_connection_error_exits_with_friendly_message(self, monkeypatch):
        # Bug 1: dulu hanya requests.HTTPError yang ditangkap, ConnectionError/Timeout
        # akan lolos jadi traceback mentah. Sekarang harus exit rapi (SystemExit),
        # bukan raise ConnectionError langsung ke pemanggil.
        def fake_get_story_info(story_id):
            raise requests.ConnectionError("koneksi putus")

        monkeypatch.setattr(app_mod.api, "get_story_info", fake_get_story_info)
        with pytest.raises(SystemExit):
            app_mod.fetch_story_or_exit("12345")

    def test_timeout_exits_with_friendly_message(self, monkeypatch):
        def fake_get_story_info(story_id):
            raise requests.Timeout("waktu habis")

        monkeypatch.setattr(app_mod.api, "get_story_info", fake_get_story_info)
        with pytest.raises(SystemExit):
            app_mod.fetch_story_or_exit("12345")


class TestResolveSaveDir:
    def test_fallback_oserror_exits_cleanly(self, monkeypatch, tmp_path):
        # Bug 4: fallback ke get_default_download_dir() dulu bisa raise OSError
        # tanpa tertangkap. Sekarang harus exit rapi (SystemExit), bukan crash mentah.
        def fail_mkdir(self, parents=False, exist_ok=False):
            raise OSError("folder tidak writable")

        def fail_default_dir():
            raise OSError("home dir tidak writable")

        monkeypatch.setattr(pathlib.Path, "mkdir", fail_mkdir)
        monkeypatch.setattr(app_mod.cli, "get_default_download_dir", fail_default_dir)

        with pytest.raises(SystemExit):
            app_mod.resolve_save_dir(str(tmp_path / "subfolder"), {})


class TestResetSteps:
    def test_reset_steps_resets_counter(self):
        cli_mod.reset_steps()
        cli_mod.step_rule("Langkah Satu")
        cli_mod.step_rule("Langkah Dua")
        assert cli_mod._step_counter["n"] == 2

        cli_mod.reset_steps()
        assert cli_mod._step_counter["n"] == 0
