"""
Unit test untuk fungsi-fungsi murni (pure function) di wattpdl.py.
Jalankan dengan: pytest
"""
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from api import extract_story_id
from cli import format_duration, parse_chapter_selection
from writers import html_to_text, safe_filename


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
