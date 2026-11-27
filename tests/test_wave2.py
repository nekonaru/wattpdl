"""
Wave 2 regression tests: search filters/JSON, author info, history,
PDF/EPUB options and new validation rules.
"""
import json

import pytest

from wattpdl import app as app_mod
from wattpdl import cli_args, library, writers

FAKE_RESULTS = [
    {"id": "1", "title": "Zebra", "author": "a", "num_parts": 5, "completed": True,
     "votes": 10, "language": "English", "create_date": "2020-01-01", "modify_date": "2020-02-01"},
    {"id": "2", "title": "Alpha", "author": "b", "num_parts": 50, "completed": False,
     "votes": 100, "language": "Indonesian", "create_date": "2021-01-01", "modify_date": "2021-02-01"},
    {"id": "3", "title": "Middle", "author": "c", "num_parts": 20, "completed": True,
     "votes": 50, "language": "English", "create_date": "2022-01-01", "modify_date": "2022-02-01"},
]


@pytest.fixture(autouse=True)
def isolate(monkeypatch, tmp_path):
    monkeypatch.setattr(app_mod.api, "search_stories", lambda *a, **kw: list(FAKE_RESULTS))
    monkeypatch.setattr(app_mod.api, "get_author_stories", lambda *a, **kw: [
        {"id": "1", "title": "A", "num_parts": 3, "completed": True},
        {"id": "2", "title": "B", "num_parts": 9, "completed": False},
    ])
    monkeypatch.setattr(library, "HISTORY_FILE", tmp_path / "history.json")
    monkeypatch.setattr(app_mod, "run_download", lambda *a, **kw: None)


class TestSearchFilters:
    def test_json_output_lists_all_results(self, monkeypatch, capsys):
        args = cli_args.parse_args(["--search", "x", "--json"])
        app_mod.run_search(args)
        assert [x["id"] for x in json.loads(capsys.readouterr().out)] == ["1", "2", "3"]

    def test_status_filter(self, monkeypatch, capsys):
        args = cli_args.parse_args(["--search", "x", "--json", "--search-status", "completed"])
        app_mod.run_search(args)
        assert [x["id"] for x in json.loads(capsys.readouterr().out)] == ["1", "3"]

    def test_min_chapters_filter(self, monkeypatch, capsys):
        args = cli_args.parse_args(["--search", "x", "--json", "--search-min-chapters", "20"])
        app_mod.run_search(args)
        assert [x["id"] for x in json.loads(capsys.readouterr().out)] == ["2", "3"]

    def test_language_filter(self, monkeypatch, capsys):
        args = cli_args.parse_args(["--search", "x", "--json", "--search-language", "English"])
        app_mod.run_search(args)
        assert [x["id"] for x in json.loads(capsys.readouterr().out)] == ["1", "3"]

    def test_sort_votes(self, monkeypatch, capsys):
        args = cli_args.parse_args(["--search", "x", "--json", "--search-sort", "votes"])
        app_mod.run_search(args)
        assert [x["id"] for x in json.loads(capsys.readouterr().out)] == ["2", "3", "1"]

    def test_sort_title(self, monkeypatch, capsys):
        args = cli_args.parse_args(["--search", "x", "--json", "--search-sort", "title"])
        app_mod.run_search(args)
        assert [x["id"] for x in json.loads(capsys.readouterr().out)] == ["2", "3", "1"]


class TestAuthorInfo:
    def test_author_info_json(self, capsys):
        args = cli_args.parse_args(["--author-info", "nekonaru", "--json"])
        app_mod.run_author_info(args)
        assert len(json.loads(capsys.readouterr().out)) == 2

    def test_author_info_table(self):
        args = cli_args.parse_args(["--author-info", "nekonaru"])
        app_mod.run_author_info(args)


class TestHistory:
    def test_record_and_load(self):
        library.record_download("1", "Story", ["txt", "epub"], 12)
        entries = library.load_history()
        assert len(entries) == 1
        assert entries[0]["formats"] == ["txt", "epub"]
        assert entries[0]["chapters"] == 12

    def test_history_json_output(self, capsys):
        library.record_download("1", "Story", ["md"], 3)
        args = cli_args.parse_args(["--history", "--json"])
        app_mod.run_history(args)
        assert json.loads(capsys.readouterr().out)[0]["title"] == "Story"

    def test_history_empty(self):
        args = cli_args.parse_args(["--history"])
        app_mod.run_history(args)

    def test_corrupt_history_is_empty(self, tmp_path, monkeypatch):
        monkeypatch.setattr(library, "HISTORY_FILE", tmp_path / "history.json")
        library.HISTORY_FILE.write_text("{broken", encoding="utf-8")
        assert library.load_history() == []


class TestPdfAndEpubOptions:
    def test_pdf_a4_and_font_size(self, tmp_path):
        out = tmp_path / "a4.pdf"
        writers.write_combined_pdf(out, "Judul", "Penulis", "1",
                                   [(1, "Bab 1", "Isi bab.")], pagesize="A4", font_size=14)
        assert out.read_bytes().startswith(b"%PDF")

    def test_pdf_zip_options(self, tmp_path):
        out = tmp_path / "a4.zip"
        writers.write_separate_pdf_zip(out, "Judul", "Penulis", "1",
                                       [(1, "Bab 1", "Isi bab.")], pagesize="A4", font_size=12)
        assert out.exists()

    def test_epub_has_source_and_status(self, tmp_path):
        out = tmp_path / "buku.epub"
        writers.write_combined_epub(out, "Judul", "Penulis", "999",
                                    [(1, "Bab 1", "<p>Isi</p>")], meta={"completed": True})
        from ebooklib import epub

        book = epub.read_epub(str(out))
        sources = book.get_metadata("DC", "source")
        subjects = [v for v, _ in book.get_metadata("DC", "subject")]
        assert sources and "999" in sources[0][0]
        assert "Completed" in subjects


class TestNewValidation:
    def test_filters_require_search(self):
        args = cli_args.parse_args(["--search-sort", "votes"])
        with pytest.raises(ValueError):
            cli_args.validate_common_args(args)

    def test_bad_pdf_font_size(self):
        args = cli_args.parse_args(["--id", "1", "--pdf-font-size", "40"])
        with pytest.raises(ValueError):
            cli_args.validate_common_args(args)

    def test_watch_iterations_min(self):
        args = cli_args.parse_args(["--id", "1", "--watch-max-iterations", "0"])
        with pytest.raises(ValueError):
            cli_args.validate_common_args(args)

    def test_no_library_flag(self):
        args = cli_args.parse_args(["--id", "1", "--no-library"])
        assert args.no_library is True


class TestAuthorEndpointRegression:
    def test_author_url_matches_live_endpoint(self):
        # The old /stories/published path returned 404 for every real author.
        from wattpdl.api import AUTHOR_STORIES_URL

        assert "/published" not in AUTHOR_STORIES_URL
        assert AUTHOR_STORIES_URL.startswith("https://www.wattpad.com/api/v3/users/{username}/stories")


class TestWatchNotify:
    def test_watch_notify_json(self, monkeypatch, capsys, tmp_path):
        from wattpdl import config as config_mod

        monkeypatch.setattr(config_mod, "CONFIG_FILE", tmp_path / "config.json")
        counts = iter([3, 5])
        monkeypatch.setattr(app_mod.api, "get_story_info",
                            lambda story_id, timeout=None: ("T", "A", [{"id": i} for i in range(next(counts))], {}))
        monkeypatch.setattr(app_mod.time, "sleep", lambda seconds: None)
        args = cli_args.parse_args(["--id", "11", "--mode", "1", "--watch", "--watch-interval", "1",
                                    "--watch-max-iterations", "2", "--watch-notify-json", "--dry-run"])
        app_mod.run_watch(args)
        lines = [line for line in capsys.readouterr().out.splitlines() if line.startswith("{")]
        assert len(lines) == 1
        assert json.loads(lines[0])["new_chapters"] == 2


class TestNoLibrary:
    def test_no_library_skips_recording(self, monkeypatch, tmp_path):
        from wattpdl import cli as cli_mod
        from wattpdl import config as config_mod
        from wattpdl import progress as progress_mod

        monkeypatch.setattr(cli_mod, "download_chapters", lambda *a, **kw: ([(1, "Ch", "isi")], [], {}))
        monkeypatch.setattr(progress_mod, "PROGRESS_DIR", tmp_path / "progress")
        monkeypatch.setattr(config_mod, "CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.setattr(app_mod.library, "LIBRARY_FILE", tmp_path / "library.json")
        app_mod.run_download("11", "Story", "Penulis", [{"id": 1, "title": "Ch"}], "1", "1", tmp_path,
                             no_library=True, timeout=5, formats=["1"])
        assert library.load_library() == {}
        assert library.load_history() == []
