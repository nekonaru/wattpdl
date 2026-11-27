"""Shared helpers for the CLI flows.

`from_app` resolves a symbol from the public `wattpdl.app` facade at call time:
this keeps one testable seam and avoids circular imports between flows.
"""
import json
import pathlib
import sys

import requests
from rich import box
from rich.panel import Panel
from rich.table import Table

from .. import api, cli, metacache, writers
from ..cli import console
from ..i18n import t


def from_app(name):
    from .. import app
    return getattr(app, name)


def print_story_info(title: str, author: str, parts: list) -> None:
    """Print the story info panel (title, author, chapter count) shown before
    any download starts. Shared by the interactive and non-interactive flows."""
    info_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1), expand=False)
    info_table.add_column(style="muted")
    info_table.add_column(style="value")
    info_table.add_row(t("info.title"), title)
    info_table.add_row(t("info.author"), author)
    info_table.add_row(t("info.chapter_count"), str(len(parts)))
    console.print(Panel(info_table, border_style="success", box=box.ROUNDED, padding=(1, 2)))


def _ask_file_format(config: dict) -> str:
    """Ask for the output format with the same table as the interactive flow."""
    format_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1), expand=False)
    format_table.add_column(style="accent", justify="right")
    format_table.add_column(style="value")
    format_table.add_row("1", t("fmt.1"))
    format_table.add_row("2", t("fmt.2"))
    format_table.add_row("3", t("fmt.3"))
    format_table.add_row("4", t("fmt.4"))
    format_table.add_row("5", t("fmt.5"))
    console.print()
    console.print(format_table)
    return cli.Prompt.ask(
        f"\n[value]{t('prompt.format')}[/value]",
        choices=["1", "2", "3", "4", "5"],
        default=config.get("file_format", "1"),
    )


def _ask_include_images(file_format: str) -> bool:
    """Ask whether to embed inline images, like the interactive flow."""
    if file_format in ("2", "3", "5"):
        return cli.Confirm.ask(
            f"[value]{t('prompt.include_images')}[/value]",
            default=False,
        )
    return False


def resolve_save_dir(custom_path: str, config: dict, create_dirs: bool = True) -> pathlib.Path:
    """Resolve the save folder: custom path/argument wins, then the saved config, then the default Downloads folder.
    With create_dirs=False (used by --dry-run), no folder is created on disk."""
    if custom_path:
        save_dir = pathlib.Path(custom_path).expanduser().resolve()
    elif config.get("save_dir"):
        save_dir = pathlib.Path(config["save_dir"])
    else:
        save_dir = cli.get_default_download_dir()

    if not create_dirs:
        return save_dir
    try:
        save_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        console.print(f"[danger]{t('err.folder_create').lstrip()}[/danger] {e}")
        try:
            fallback = cli.get_default_download_dir()
        except OSError as e2:
            console.print(f"[danger]{t('err.folder_default_create')}[/danger] {e2}")
            console.print(f"[muted]{t('hint.other_folder')}[/muted]")
            sys.exit(1)
        console.print(f"[muted]{t('info.using_default_folder', path=fallback)}[/muted]")
        save_dir = fallback
    return save_dir


def should_skip_existing(full_path: pathlib.Path, skip_existing: bool) -> bool:
    """True if the output file already exists and skip-existing mode is on,
    used by non-interactive mode so it does not overwrite/download again unnecessarily.
    Split into a pure function so it is easy to test without mocking a full filesystem."""
    return skip_existing and full_path.exists()


def resolve_chapters(mode: str, parts: list, chapters_arg: str = None, chapter_arg: int = None) -> list:
    """Determine which chapters to download, from arguments (non-interactive) or a prompt (interactive)."""
    if mode == "3":
        if chapters_arg is not None:
            numbers = cli.parse_chapter_selection(chapters_arg, len(parts))
            console.print(f"[success]{t('ok.chapters_selected', n=len(numbers))}[/success]")
            return [(n, parts[n - 1]) for n in numbers]
        return cli.select_multiple_chapters(parts)

    if mode == "4":
        if chapter_arg is not None:
            n = chapter_arg
            if not (1 <= n <= len(parts)):
                console.print(f"[danger]{t('err.chapter_out_of_range', n=n, total=len(parts))}[/danger]")
                sys.exit(1)
            part = parts[n - 1]
            console.print(f"[success]{t('ok.selected')}[/success] Chapter {n}: {part.get('title', '')}")
            return [(n, part)]
        return [cli.select_single_chapter(parts)]

    return list(enumerate(parts, start=1))


def probe_story(story_id: str, timeout: int = None):
    """Fetch minimal story info for a status check (never raises).

    Returns (info_or_None, kind_or_None, message_or_None). Kind is `deleted`
    for 404 and `check_failed` for other API/network errors.
    """
    try:
        return api.get_story_info(story_id, timeout=timeout), None, None
    except api.StoryNotFoundError as e:
        return None, "deleted", str(e)
    except (api.StoryAccessError, requests.RequestException) as e:
        return None, "check_failed", str(e)


def probe_many(story_ids, timeout=None, workers=4) -> list:
    """Probe several stories concurrently, preserving input order."""
    from concurrent.futures import ThreadPoolExecutor

    ids = list(story_ids)
    if not ids:
        return []
    with ThreadPoolExecutor(max_workers=min(workers, len(ids))) as executor:
        return list(executor.map(lambda sid: probe_story(sid, timeout=timeout), ids))


def _fetch_story_tolerant(story_id: str, timeout: int = None):
    """Fetch a story for a batch flow (--user, --file). Returns
    (info_tuple_or_None, error_string_or_None). Unlike the single-story flow,
    a failure here must not stop the rest of the batch."""
    try:
        return api.get_story_info(story_id, timeout=timeout), None
    except (api.StoryNotFoundError, api.StoryAccessError, requests.RequestException) as e:
        return None, str(e)


def _output_base_name(title, filename) -> str:
    """The base file name for a single-story download: --filename if given, else the story title."""
    custom = (filename or "").strip()
    if custom:
        return writers.safe_filename(custom)
    return writers.safe_filename(title)


REPORT_ENTRIES = []  # reset by main(); appended after each real download


def _output_path(save_dir, base_name, mode, code, indexed_parts):
    """Output path for one (mode, format) combination.
    In mode 2 several formats need distinct zip names, hence the format suffix."""
    ext = {"2": "docx", "3": "epub", "4": "md", "5": "pdf"}.get(code, "txt")
    if mode == "1":
        return save_dir / f"{base_name}.{ext}"
    if mode == "2":
        return save_dir / (f"{base_name}.zip" if code == "1" else f"{base_name}_{ext}.zip")
    if mode == "3":
        return save_dir / f"{base_name}_selected.{ext}"
    chap_no, chap_part = indexed_parts[0]
    chap_title = writers.safe_filename(chap_part.get("title", f"Chapter {chap_no}"))
    return save_dir / f"{base_name}_Ch{chap_no:03d}_{chap_title}.{ext}"


def _write_output(path, title, author, story_id, results, mode, code,
                  meta, cover_bytes, images_by_idx, language,
                  pdf_pagesize=None, pdf_font_size=None):
    """Write the downloaded chapters to one output file in the requested format."""
    separate = mode == "2"
    if code == "2":
        writer = writers.write_separate_docx_zip if separate else writers.write_combined_docx
        writer(path, title, author, story_id, results,
               meta=meta, cover_bytes=cover_bytes, images_by_idx=images_by_idx)
    elif code == "3":
        writer = writers.write_separate_epub_zip if separate else writers.write_combined_epub
        writer(path, title, author, story_id, results,
               meta=meta, cover_bytes=cover_bytes, images_by_idx=images_by_idx, language=language)
    elif code == "4":
        writer = writers.write_separate_md_zip if separate else writers.write_combined_md
        writer(path, title, author, story_id, results, meta=meta)
    elif code == "5":
        writer = writers.write_separate_pdf_zip if separate else writers.write_combined_pdf
        options = {"pagesize": pdf_pagesize, "font_size": pdf_font_size}
        writer(path, title, author, story_id, results,
               meta=meta, cover_bytes=cover_bytes, images_by_idx=images_by_idx, **options)
    else:
        writer = writers.write_separate_zip if separate else writers.write_combined_txt
        writer(path, title, author, story_id, results)


def write_report(path, entries=None) -> None:
    """Write a download report as JSON or CSV (extension decides the format)."""
    import csv

    entries = REPORT_ENTRIES if entries is None else entries
    target = pathlib.Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.suffix.lower() == ".csv":
        fields = ["story_id", "title", "mode", "formats", "chapters", "succeeded",
                  "failed", "elapsed", "files", "at"]
        with target.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for entry in entries:
                row = dict(entry)
                row["files"] = "|".join(str(p) for p in entry.get("files", []))
                row["formats"] = ",".join(entry.get("formats", []))
                writer.writerow({k: row.get(k, "") for k in fields})
    else:
        target.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")

def warn_if_parts_missing(parts: list, meta: dict) -> None:
    """Wattpad reports how many chapters a story has (numParts). If fewer are
    actually listed, some are hidden, paid, or unpublished and cannot be
    downloaded. Tell the user instead of silently producing an incomplete file."""
    reported = (meta or {}).get("num_parts")
    if isinstance(reported, int) and reported > len(parts):
        console.print(f"[warning]{t('warn.parts_mismatch', reported=reported, accessible=len(parts))}[/warning]")


def fetch_cover(meta: dict, no_cover: bool, file_format: str, timeout: int = None):
    """Download the story cover (only for formats that embed it), with a spinner so
    the program never looks frozen while waiting for the network."""
    if no_cover or file_format not in ("2", "3", "5") or not meta.get("cover_url"):
        return None
    with console.status(f"[accent]{t('status.downloading_cover')}[/accent]", spinner="dots"):
        return api.download_cover_image(meta["cover_url"], timeout=timeout)


def fetch_story_or_exit(story_id: str, use_cache: bool = True, timeout: int = None):
    if use_cache:
        cached = metacache.get_cached_story(story_id)
        if cached:
            warn_if_parts_missing(cached[2], cached[3])
            return cached

    with console.status(f"[accent]{t('status.fetching_story', story_id=story_id)}[/accent]", spinner="dots"):
        try:
            title, author, parts, meta = api.get_story_info(story_id, timeout=timeout)
        except (api.StoryNotFoundError, api.StoryAccessError) as e:
            # The message is already specific from api.py (distinguishes 404 vs 403/401), show it as-is.
            console.print(f"[danger]❌  {e}[/danger]")
            sys.exit(1)
        except requests.RequestException as e:
            console.print(f"[danger]{t('err.api_access')}[/danger] {e}")
            console.print(f"[muted]{t('hint.check_connection')}[/muted]")
            sys.exit(1)

    if not parts:
        console.print(f"[danger]{t('err.no_chapters')}[/danger]")
        sys.exit(1)

    warn_if_parts_missing(parts, meta)
    if use_cache:
        metacache.save_story_cache(story_id, title, author, parts, meta)
    return title, author, parts, meta

def _search_table(stories: list, start: int, end: int) -> Table:
    """One page of search results, numbered globally (start..end, 1-based)."""
    table = Table(box=box.SIMPLE_HEAD, padding=(0, 1), expand=False)
    table.add_column(t("table.no"), style="muted", justify="right", width=5)
    table.add_column(t("table.title"), style="value")
    table.add_column(t("table.author"), style="muted")
    table.add_column(t("table.chapters"), style="muted", justify="right")
    table.add_column(t("table.status"), style="muted")
    for i in range(start, end):
        s = stories[i]
        table.add_row(
            str(i + 1),
            s["title"],
            s["author"],
            str(s["num_parts"]),
            t("info.status_completed") if s["completed"] else t("info.status_ongoing"),
        )
    return table
