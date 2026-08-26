"""
Unit test untuk fungsi-fungsi murni (pure function) di package wattpdl.
Jalankan dengan: pytest
(path ke src/ sudah diatur lewat [tool.pytest.ini_options] di pyproject.toml)
"""
import pathlib
import tempfile

import pytest
import requests
import responses as responses_lib

from wattpdl import api as api_mod
from wattpdl import app as app_mod
from wattpdl import cli as cli_mod
from wattpdl import cli_args
from wattpdl import config as config_mod
from wattpdl import progress as progress_mod
from wattpdl.api import extract_story_id, get_chapter_html
from wattpdl.cli import format_duration, parse_chapter_selection
from wattpdl.writers import (
    html_to_text,
    safe_filename,
    write_combined_epub,
    write_combined_md,
    write_separate_epub_zip,
    write_separate_md_zip,
)


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

    def test_huge_range_does_not_hang(self):
        # Bug: dulu range(start, end+1) dibuat penuh SEBELUM difilter ke [1, total],
        # jadi rentang seperti "1-500000000" bikin CLI hang lama walau cerita cuma
        # 10 chapter. Sekarang harus dipangkas dulu, jadi selesai hampir instan
        # berapa pun besar angka yang diketik user.
        import time

        start = time.time()
        result = parse_chapter_selection("1-999999999999999", total=10)
        elapsed = time.time() - start

        assert result == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        assert elapsed < 1.0, f"parse_chapter_selection terlalu lambat: {elapsed:.2f}s"

    def test_huge_range_partially_overlapping_total(self):
        # Batas bawah normal, batas atas raksasa -> tetap harus dipangkas ke total.
        assert parse_chapter_selection("8-999999999999999", total=10) == [8, 9, 10]


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
        assert cli_args.FORMAT_TO_CODE == {"txt": "1", "docx": "2", "epub": "3", "md": "4"}


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


class TestMarkdownWriter:
    """Fitur baru: format .md sebagai pilihan ke-4."""

    @pytest.fixture
    def sample_results(self):
        return [
            (1, "Chapter Awal", "Paragraf pertama.\n\nParagraf kedua."),
            (2, "Chapter Tengah", "Isi chapter dua."),
        ]

    def test_combined_md_contains_title_and_chapters(self, tmp_path, sample_results):
        out = tmp_path / "cerita.md"
        write_combined_md(out, "Judul Cerita", "Penulis A", "999", sample_results,
                           meta={"tags": ["Romance", "Drama"], "description": "Sinopsis singkat."})

        content = out.read_text(encoding="utf-8")
        assert "# Judul Cerita" in content
        assert "Penulis A" in content
        assert "Romance, Drama" in content
        assert "Sinopsis singkat." in content
        assert "## Chapter Awal" in content
        assert "## Chapter Tengah" in content
        assert "Paragraf pertama." in content

    def test_combined_md_without_meta_does_not_crash(self, tmp_path, sample_results):
        out = tmp_path / "cerita.md"
        write_combined_md(out, "Judul", "Penulis", "999", sample_results)
        assert out.exists()

    def test_separate_md_zip_has_one_file_per_chapter_plus_info(self, tmp_path, sample_results):
        import zipfile

        out = tmp_path / "cerita.zip"
        write_separate_md_zip(out, "Judul", "Penulis", "999", sample_results)

        with zipfile.ZipFile(out) as zf:
            names = zf.namelist()
            assert "000_info.md" in names
            assert any(n.endswith("_Chapter_Awal.md") for n in names)
            assert any(n.endswith("_Chapter_Tengah.md") for n in names)


class TestSkipExisting:
    """Fitur baru: lewati unduhan kalau file output sudah ada."""

    def test_skips_when_file_exists_and_flag_on(self, tmp_path):
        existing = tmp_path / "sudah_ada.txt"
        existing.write_text("isi lama")
        assert app_mod.should_skip_existing(existing, skip_existing=True) is True

    def test_does_not_skip_when_flag_off(self, tmp_path):
        existing = tmp_path / "sudah_ada.txt"
        existing.write_text("isi lama")
        assert app_mod.should_skip_existing(existing, skip_existing=False) is False

    def test_does_not_skip_when_file_missing(self, tmp_path):
        missing = tmp_path / "belum_ada.txt"
        assert app_mod.should_skip_existing(missing, skip_existing=True) is False


class TestCoverImage:
    """Fitur baru: unduh cover cerita untuk disisipkan ke .docx/.epub."""

    def test_download_cover_image_returns_none_without_url(self):
        assert api_mod.download_cover_image(None) is None
        assert api_mod.download_cover_image("") is None

    def test_download_cover_image_returns_none_on_request_failure(self, monkeypatch):
        def fake_get(*args, **kwargs):
            raise requests.ConnectionError("gagal konek")

        monkeypatch.setattr(api_mod.requests, "get", fake_get)
        # Kegagalan unduh cover TIDAK boleh menghentikan proses (cover cuma pemanis).
        assert api_mod.download_cover_image("https://example.com/cover.jpg") is None

    @responses_lib.activate
    def test_download_cover_image_returns_bytes_on_success(self):
        responses_lib.add(
            responses_lib.GET, "https://example.com/cover.jpg",
            body=b"\xff\xd8\xff\xe0FAKEJPEGDATA", status=200,
        )
        result = api_mod.download_cover_image("https://example.com/cover.jpg")
        assert result == b"\xff\xd8\xff\xe0FAKEJPEGDATA"

    def test_epub_cover_insert_failure_does_not_raise(self):
        from wattpdl.writers import _build_epub_book, _set_epub_cover

        book, epub = _build_epub_book("Judul", "Penulis", "999")
        # Byte acak yang bukan gambar valid — pastikan tidak melempar exception,
        # karena kegagalan sisip cover tidak boleh menggagalkan seluruh file.
        _set_epub_cover(book, epub, b"bukan-gambar-valid")


class TestEpubMetadata:
    """Fitur baru: metadata EPUB lebih lengkap (genre/tags, deskripsi, tanggal terbit)."""

    def test_combined_epub_includes_description_and_tags_and_date(self, tmp_path):
        out = tmp_path / "cerita.epub"
        meta = {
            "description": "Ini sinopsis cerita.",
            "tags": ["Fantasy", "Adventure"],
            "create_date": "2020-01-01",
        }
        write_combined_epub(out, "Judul", "Penulis", "999",
                             [(1, "Bab 1", "Isi bab satu.")], meta=meta)

        from ebooklib import epub

        book = epub.read_epub(str(out))
        descriptions = [v for v, _ in book.get_metadata("DC", "description")]
        subjects = [v for v, _ in book.get_metadata("DC", "subject")]
        dates = [v for v, _ in book.get_metadata("DC", "date")]

        assert descriptions == ["Ini sinopsis cerita."]
        assert subjects == ["Fantasy", "Adventure"]
        assert dates == ["2020-01-01"]

    def test_combined_epub_without_meta_has_no_extra_metadata(self, tmp_path):
        out = tmp_path / "cerita.epub"
        write_combined_epub(out, "Judul", "Penulis", "999", [(1, "Bab 1", "Isi.")])

        from ebooklib import epub

        book = epub.read_epub(str(out))
        assert book.get_metadata("DC", "description") == []
        assert book.get_metadata("DC", "subject") == []

    def test_separate_epub_zip_info_book_has_metadata(self, tmp_path):
        import zipfile

        from ebooklib import epub

        out = tmp_path / "cerita.zip"
        meta = {"description": "Sinopsis.", "tags": ["Horror"]}
        write_separate_epub_zip(out, "Judul", "Penulis", "999",
                                 [(1, "Bab 1", "Isi bab satu.")], meta=meta)

        with zipfile.ZipFile(out) as zf:
            info_bytes = zf.read("000_info.epub")
            info_path = tmp_path / "000_info.epub"
            info_path.write_bytes(info_bytes)
            book = epub.read_epub(str(info_path))
            descriptions = [v for v, _ in book.get_metadata("DC", "description")]
            assert descriptions == ["Sinopsis."]


class TestIntegrationMockHttp:
    """
    Integration test yang mem-mock HTTP di level `requests` (pakai `responses`),
    bukan cuma unit test fungsi murni — memastikan pipeline API -> writer
    utuh berjalan seperti pemakaian nyata.
    """

    @responses_lib.activate
    def test_full_pipeline_story_info_to_chapter_download(self):
        story_json = {
            "title": "Cerita Uji Coba",
            "description": "Deskripsi cerita uji coba.",
            "cover": "https://example.com/cover.jpg",
            "tags": ["Fantasy"],
            "createDate": "2021-05-01",
            "user": {"name": "Penulis Uji"},
            "numParts": 2,
            "parts": [
                {"id": 111, "title": "Bab Satu"},
                {"id": 222, "title": "Bab Dua"},
            ],
        }
        responses_lib.add(
            responses_lib.GET,
            api_mod.STORY_INFO_URL.format(story_id="999"),
            json=story_json, status=200,
        )
        responses_lib.add(
            responses_lib.GET,
            api_mod.CHAPTER_TEXT_URL.format(part_id=111),
            body="<p>Ini isi bab satu.</p>", status=200,
        )
        responses_lib.add(
            responses_lib.GET,
            api_mod.CHAPTER_TEXT_URL.format(part_id=222),
            body="<p>Ini isi bab dua.</p>", status=200,
        )
        responses_lib.add(
            responses_lib.GET, "https://example.com/cover.jpg",
            body=b"FAKEJPEGBYTES", status=200,
        )

        title, author, parts, meta = api_mod.get_story_info("999")
        assert title == "Cerita Uji Coba"
        assert author == "Penulis Uji"
        assert len(parts) == 2
        assert meta["description"] == "Deskripsi cerita uji coba."
        assert meta["tags"] == ["Fantasy"]

        cover_bytes = api_mod.download_cover_image(meta["cover_url"])
        assert cover_bytes == b"FAKEJPEGBYTES"

        html1 = api_mod.get_chapter_html(parts[0]["id"])
        html2 = api_mod.get_chapter_html(parts[1]["id"])
        assert html_to_text(html1) == "Ini isi bab satu."
        assert html_to_text(html2) == "Ini isi bab dua."

    @responses_lib.activate
    def test_full_pipeline_handles_api_error_gracefully(self):
        responses_lib.add(
            responses_lib.GET,
            api_mod.STORY_INFO_URL.format(story_id="404"),
            status=404,
        )
        with pytest.raises(requests.HTTPError):
            api_mod.get_story_info("404")
