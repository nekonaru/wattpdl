"""
WattPDL: Wattpad Story Downloader
Main entry point. Two modes:
  - Interactive     : wattpdl                       (no arguments, question and answer in the terminal)
  - Non-interactive : wattpdl --id ... --mode ...     (for scripting/automation)
Flow: take input (prompt or arguments) -> fetch data (api.py) -> write the file
(writers.py) -> show progress (cli.py). Preferences are saved through
config.py, and download progress through progress.py for the resume feature.
"""
import json
import pathlib
import sys
import time

import requests
from rich import box
from rich.align import Align
from rich.panel import Panel
from rich.table import Table

from . import api, cli, cli_args, library, metacache, updater, writers
from . import config as config_mod
from . import progress as progress_mod
from .cli import console, step_rule
from .i18n import t


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


def run_download(story_id, title, author, parts, mode, file_format, save_dir,
                  chapters_arg=None, chapter_arg=None, meta=None, cover_bytes=None,
                  skip_existing=False, interactive=False, workers=1, include_images=False,
                  language="id", retries=None, timeout=None, dry_run=False,
                  keep_progress_on_success=False):
    """Shared download flow for both interactive and non-interactive modes."""
    indexed_parts = resolve_chapters(mode, parts, chapters_arg, chapter_arg)

    ext = {"2": "docx", "3": "epub", "4": "md", "5": "pdf"}.get(file_format, "txt")
    base_name = writers.safe_filename(title)

    if mode == "1":
        full_path = save_dir / f"{base_name}.{ext}"
    elif mode == "2":
        full_path = save_dir / f"{base_name}.zip"
    elif mode == "3":
        full_path = save_dir / f"{base_name}_selected.{ext}"
    else:
        chap_no, chap_part = indexed_parts[0]
        chap_title = writers.safe_filename(chap_part.get("title", f"Chapter {chap_no}"))
        full_path = save_dir / f"{base_name}_Ch{chap_no:03d}_{chap_title}.{ext}"

    try:
        path_exists = full_path.exists()
    except OSError as e:
        # This can happen if the combined file name (story title + chapter title
        # for mode 4, or the target folder chosen by the user is already long)
        # still exceeds the operating system's path length limit even after being truncated
        # by safe_filename(). Show a tidy message, do not let a raw traceback through.
        console.print(f"[danger]{t('err.path_invalid')}[/danger] {e}")
        console.print(f"[muted]{t('info.path_tried', path=full_path)}[/muted]")
        console.print(f"[muted]{t('hint.shorter_path')}[/muted]")
        sys.exit(1)

    if dry_run:
        reused, to_download = 0, 0
        if story_id:
            store = progress_mod.ProgressStore(story_id)
            for _, part in indexed_parts:
                if store.has(part["id"]):
                    reused += 1
                else:
                    to_download += 1
        else:
            to_download = len(indexed_parts)
        ext = {"2": "docx", "3": "epub", "4": "md", "5": "pdf"}.get(file_format, "txt")
        console.print(f"[warning]{t('dryrun.title')}[/warning]")
        console.print(f"[muted]{t('dryrun.path')}[/muted] [accent]{full_path}[/accent]")
        console.print(f"[muted]{t('dryrun.exists')}[/muted] [accent]{str(path_exists).lower()}[/accent]")
        console.print(f"[muted]{t('dryrun.mode')}[/muted] [accent]{mode} ({ext})[/accent]")
        console.print(f"[muted]{t('dryrun.chapters')}[/muted] [accent]{len(indexed_parts)}[/accent]")
        console.print(f"[muted]{t('dryrun.reused')}[/muted] [accent]{reused}[/accent]")
        console.print(f"[muted]{t('dryrun.to_download')}[/muted] [accent]{to_download}[/accent]")
        return

    if path_exists:
        if interactive:
            if not cli.confirm_overwrite(full_path):
                console.print(f"[muted]{t('info.skipped_existing_kept')}[/muted]")
                return
        elif should_skip_existing(full_path, skip_existing):
            console.print(
                f"[muted]{t('info.skipped_existing')}[/muted] [accent]{full_path}[/accent]\n"
                f"[muted]{t('hint.remove_skip_existing')}[/muted]"
            )
            return

    console.print(f"[value]{t('info.saved_at')}[/value] [accent]{full_path}[/accent]")

    step_rule(t("step.downloading"))
    start_time = time.time()
    rate_limiter = api.AdaptiveRateLimiter()
    results, failed_chapters, images_by_idx = cli.download_chapters(
        indexed_parts, story_id=story_id, max_workers=workers,
        rate_limiter=rate_limiter, include_images=include_images,
        retries=retries, timeout=timeout,
    )
    elapsed = cli.format_duration(time.time() - start_time)
    if include_images:
        n_images = sum(len(v) for v in images_by_idx.values())
        if n_images:
            console.print(f"[muted]{t('info.images_downloaded', n=n_images)}[/muted]")
        else:
            console.print(f"[warning]{t('warn.no_images')}[/warning]")

    try:
        if mode == "2":
            if file_format == "2":
                writers.write_separate_docx_zip(full_path, title, author, story_id, results,
                                                 meta=meta, cover_bytes=cover_bytes, images_by_idx=images_by_idx)
            elif file_format == "3":
                writers.write_separate_epub_zip(full_path, title, author, story_id, results,
                                                 meta=meta, cover_bytes=cover_bytes,
                                                 images_by_idx=images_by_idx, language=language)
            elif file_format == "4":
                writers.write_separate_md_zip(full_path, title, author, story_id, results, meta=meta)
            elif file_format == "5":
                writers.write_separate_pdf_zip(full_path, title, author, story_id, results,
                                                meta=meta, cover_bytes=cover_bytes, images_by_idx=images_by_idx)
            else:
                writers.write_separate_zip(full_path, title, author, story_id, results)
        else:
            if file_format == "2":
                writers.write_combined_docx(full_path, title, author, story_id, results,
                                             meta=meta, cover_bytes=cover_bytes, images_by_idx=images_by_idx)
            elif file_format == "3":
                writers.write_combined_epub(full_path, title, author, story_id, results,
                                             meta=meta, cover_bytes=cover_bytes,
                                             images_by_idx=images_by_idx, language=language)
            elif file_format == "4":
                writers.write_combined_md(full_path, title, author, story_id, results, meta=meta)
            elif file_format == "5":
                writers.write_combined_pdf(full_path, title, author, story_id, results,
                                            meta=meta, cover_bytes=cover_bytes, images_by_idx=images_by_idx)
            else:
                writers.write_combined_txt(full_path, title, author, story_id, results)
    except OSError as e:
        # The chapters were already downloaded (and their progress already saved through
        # progress.py), so a failure to WRITE the file at the last second
        # (path too long, disk full, no write permission, etc.) must not appear
        # as a raw traceback. Tell the user their progress is not lost.
        console.print(f"[danger]{t('err.write_failed')}[/danger] {e}")
        console.print(f"[muted]{t('info.path_tried', path=full_path)}[/muted]")
        console.print(f"[muted]{t('hint.progress_kept')}[/muted]")
        sys.exit(1)

    step_rule(t("step.summary"))
    summary = Table(show_header=False, box=box.SIMPLE, padding=(0, 1), expand=False)
    summary.add_column(style="muted")
    summary.add_column(style="value")
    summary.add_row(t("sum.file_saved"), f"[accent]{full_path}[/accent]")
    summary.add_row(t("sum.success"), f"[success]{len(results) - len(failed_chapters)}/{len(results)}[/success]")
    if failed_chapters:
        summary.add_row(t("sum.failed"), f"[danger]{len(failed_chapters)}[/danger]")
    summary.add_row(t("sum.total_time"), elapsed)

    if failed_chapters:
        fail_list = "\n".join(f"[danger]• {ch}[/danger]" for ch in failed_chapters)
        body = Table.grid(padding=(0, 0))
        body.add_row(summary)
        body.add_row("")
        body.add_row(f"[muted]{t('sum.failed_chapters')}[/muted]\n{fail_list}")
        console.print(Panel(
            body,
            title=f"[warning]{t('sum.title_partial')}[/warning]",
            border_style="warning",
            box=box.ROUNDED,
            padding=(1, 2),
        ))
        console.print(f"[muted]{t('sum.partial_hint')}[/muted]\n")
    else:
        # All chapters succeeded -> this story's resume progress file is no longer needed,
        # unless the caller wants to keep it (used by --update-library so the next update
        # only fetches the chapters that were added since).
        if not keep_progress_on_success:
            progress_mod.clear_progress(story_id)
        if mode in ("1", "2"):
            # Record it in the library so --check-updates / --watch can detect
            # when this story gets new chapters later.
            library.remember_story(story_id, title, len(parts))
        console.print(Panel(
            summary,
            title=f"[success]{t('sum.title_done')}[/success]",
            border_style="success",
            box=box.DOUBLE,
            padding=(1, 2),
        ))
        console.print()

    # save the format & save folder preferences for the next session
    config_mod.save_config(save_dir=str(save_dir), file_format=file_format)


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


def run_non_interactive(args):
    cli.reset_steps()
    try:
        cli_args.validate_non_interactive_args(args)
    except ValueError as e:
        console.print(f"[danger]❌  {e}[/danger]")
        sys.exit(1)

    try:
        story_id = api.extract_story_id(args.id)
    except ValueError as e:
        console.print(f"[danger]❌  {e}[/danger]")
        sys.exit(1)

    config = config_mod.load_config()
    title, author, parts, meta = fetch_story_or_exit(story_id, use_cache=not args.no_cache, timeout=args.timeout)

    step_rule(t("step.story_info"))
    print_story_info(title, author, parts)

    file_format = cli_args.FORMAT_TO_CODE[args.format] if args.format else config.get("file_format", "1")
    if not args.dry_run:
        writers.check_format_libraries(file_format, console)

    save_dir = resolve_save_dir(args.output_dir, config, create_dirs=not args.dry_run)

    cover_bytes = None if args.dry_run else fetch_cover(meta, args.no_cover, file_format, timeout=args.timeout)

    run_download(
        story_id, title, author, parts, args.mode, file_format, save_dir,
        chapters_arg=args.chapters, chapter_arg=args.chapter,
        meta=meta, cover_bytes=cover_bytes, skip_existing=args.skip_existing,
        workers=args.workers, include_images=args.include_images, language=args.lang,
        retries=args.retries, timeout=args.timeout, dry_run=args.dry_run,
    )


def run_interactive(args=None):
    cli.reset_steps()
    dry_run = args.dry_run if args else False
    retries = args.retries if args else None
    timeout = args.timeout if args else None
    console.print()
    console.print(Align.center(cli.LOGO))
    console.print(
        Align.center(
            f"[value]{t('tagline')}[/value]  [muted]{t('tagline_sub')}[/muted]"
        )
    )

    config = config_mod.load_config()

    step_rule(t("step.enter_story"))
    raw = cli.Prompt.ask(f"[value]{t('prompt.story')}[/value]")
    try:
        story_id = api.extract_story_id(raw)
    except ValueError as e:
        console.print(f"\n[danger]❌  {e}[/danger]")
        sys.exit(1)

    title, author, parts, meta = fetch_story_or_exit(story_id, timeout=timeout)

    step_rule(t("step.story_info"))
    print_story_info(title, author, parts)

    step_rule(t("step.pick_mode"))
    mode_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1), expand=False)
    mode_table.add_column(style="accent", justify="right")
    mode_table.add_column(style="value")
    mode_table.add_row("1", t("mode.1"))
    mode_table.add_row("2", t("mode.2"))
    mode_table.add_row("3", t("mode.3"))
    mode_table.add_row("4", t("mode.4"))
    console.print(mode_table)

    mode = cli.Prompt.ask(f"\n[value]{t('prompt.mode')}[/value]", choices=["1", "2", "3", "4"], default="1")

    file_format = _ask_file_format(config)
    if not dry_run:
        writers.check_format_libraries(file_format, console)

    include_images = _ask_include_images(file_format)

    # The actual chapter selection (including the prompt for mode 3/4) happens inside
    # run_download() -> resolve_chapters(). Here len(parts) is enough as a
    # rough estimate for offering parallel mode, accurate enough because modes 1/2
    # do download every chapter, and asking this is harmless
    # even if the user later picks only a few chapters in mode 3/4.
    workers = 1
    if len(parts) > 3:
        use_parallel = cli.Confirm.ask(
            f"[value]{t('prompt.parallel')}[/value]",
            default=False,
        )
        if use_parallel:
            workers = cli.IntPrompt.ask(
                f"[muted]{t('prompt.workers')}[/muted]", default=4
            )

    step_rule(t("step.save_folder"))
    interactive_default = args.output_dir if (args and args.output_dir) else config.get("save_dir")
    default_dir = pathlib.Path(interactive_default) if interactive_default else cli.get_default_download_dir()
    console.print(f"[muted]{t('info.default_folder')}[/muted] [accent]{default_dir}[/accent]")
    custom = cli.Prompt.ask(
        f"[muted]{t('prompt.custom_folder')}[/muted]",
        default="",
        show_default=False,
    ).strip()
    save_dir = resolve_save_dir(custom or (args.output_dir if args else ""), config, create_dirs=not dry_run)

    # Fetched after every question was answered: a silent network wait between
    # prompts makes people press Enter again, which then answers the next prompts.
    cover_bytes = None if dry_run else fetch_cover(meta, False, file_format, timeout=timeout)

    run_download(story_id, title, author, parts, mode, file_format, save_dir,
                 meta=meta, cover_bytes=cover_bytes, interactive=True,
                 workers=workers, include_images=include_images,
                 retries=retries, timeout=timeout, dry_run=dry_run)


def run_user_mode(args) -> None:
    """Download all/selected stories from one Wattpad author at once (--user).
    Always non-interactive: which stories are downloaded is decided through --user-select,
    and each story is downloaded in mode 1 (combined) or 2 (separate zip); modes 3/4
    (picking specific chapters) do not apply to many stories at once.
    """
    cli.reset_steps()
    mode = args.mode or "1"
    if mode not in ("1", "2"):
        console.print(f"[danger]{t('err.user_mode_only_12')}[/danger]")
        sys.exit(1)

    step_rule(t("step.story_list", user=args.user))
    try:
        with console.status(f"[accent]{t('status.fetching_user_stories', user=args.user)}[/accent]", spinner="dots"):
            stories = api.get_author_stories(args.user, timeout=args.timeout)
    except (api.StoryNotFoundError, api.StoryAccessError) as e:
        console.print(f"[danger]❌  {e}[/danger]")
        sys.exit(1)
    except requests.RequestException as e:
        console.print(f"[danger]{t('err.api_access')}[/danger] {e}")
        sys.exit(1)

    if not stories:
        console.print(f"[danger]{t('err.no_user_stories', user=args.user)}[/danger]")
        sys.exit(1)

    table = Table(box=box.SIMPLE_HEAD, padding=(0, 1), expand=False)
    table.add_column(t("table.no"), style="muted", justify="right", width=5)
    table.add_column(t("table.title"), style="value")
    table.add_column(t("table.chapters"), style="muted", justify="right")
    for i, s in enumerate(stories, start=1):
        table.add_row(str(i), s["title"], str(s["num_parts"]))
    console.print(table)

    if args.user_select.strip().lower() == "all":
        chosen_indices = list(range(1, len(stories) + 1))
    else:
        try:
            chosen_indices = cli.parse_chapter_selection(args.user_select, len(stories))
        except ValueError as e:
            console.print(f"[danger]{t('err.user_select_invalid', error=e)}[/danger]")
            sys.exit(1)

    console.print(f"[success]{t('ok.stories_selected', n=len(chosen_indices), total=len(stories))}[/success]")

    config = config_mod.load_config()
    file_format = cli_args.FORMAT_TO_CODE[args.format] if args.format else config.get("file_format", "1")
    if not args.dry_run:
        writers.check_format_libraries(file_format, console)
    save_dir = resolve_save_dir(args.output_dir, config, create_dirs=not args.dry_run)

    for n, story_index in enumerate(chosen_indices, start=1):
        story_summary = stories[story_index - 1]
        console.print(f"[primary]{t('info.story_progress', n=n, total=len(chosen_indices), title=story_summary['title'])}[/primary]")
        cli.reset_steps()  # reset the step numbering for every new story, instead of keeping on counting across stories
        title, author, parts, meta = fetch_story_or_exit(story_summary["id"], use_cache=not args.no_cache, timeout=args.timeout)

        cover_bytes = None if args.dry_run else fetch_cover(meta, args.no_cover, file_format, timeout=args.timeout)

        run_download(
            story_summary["id"], title, author, parts, mode, file_format, save_dir,
            meta=meta, cover_bytes=cover_bytes, skip_existing=args.skip_existing,
            workers=args.workers, include_images=args.include_images, language=args.lang,
            retries=args.retries, timeout=args.timeout, dry_run=args.dry_run,
        )

    config_mod.save_config(save_dir=str(save_dir), file_format=file_format)


def run_check_updates(args=None) -> None:
    """Check every story that was fully downloaded before (recorded in library.json)
    for new chapters on Wattpad right now. It downloads nothing,
    only reports; the user just runs the normal download again for the stories
    they want to update. With `--json`, prints a machine-readable JSON array
    to stdout instead of the table (for scripting).
    """
    cli.reset_steps()
    as_json = bool(args and args.json)
    timeout = args.timeout if args else None
    if not as_json:
        step_rule(t("step.check_updates"))
    saved = library.load_library()
    if not saved:
        if as_json:
            print("[]")
            return
        console.print(f"[muted]{t('info.library_empty')}[/muted]")
        return

    entries = []
    table = None
    if not as_json:
        table = Table(box=box.SIMPLE_HEAD, padding=(0, 1), expand=False)
        table.add_column(t("table.title"), style="value")
        table.add_column(t("table.recorded_chapters"), style="muted", justify="right")
        table.add_column(t("table.current_chapters"), style="muted", justify="right")
        table.add_column(t("table.status"), style="value")

    any_update = False
    for story_id, entry in saved.items():
        title = entry.get("title", story_id)
        old_count = entry.get("num_parts", 0)
        base = {"id": str(story_id), "title": title, "recorded_parts": old_count}
        try:
            _, _, parts, _ = api.get_story_info(story_id, timeout=timeout)
            new_count = len(parts)
        except api.StoryNotFoundError:
            entries.append({**base, "current_parts": None, "status": "deleted", "new_chapters": 0})
            if not as_json:
                table.add_row(title, str(old_count), "-", f"[danger]{t('status.deleted')}[/danger]")
            continue
        except (api.StoryAccessError, requests.RequestException):
            entries.append({**base, "current_parts": None, "status": "check_failed", "new_chapters": 0})
            if not as_json:
                table.add_row(title, str(old_count), "?", f"[warning]{t('status.check_failed')}[/warning]")
            continue

        if new_count > old_count:
            any_update = True
            entries.append({**base, "current_parts": new_count, "status": "new_chapters", "new_chapters": new_count - old_count})
            if not as_json:
                status = f"[success]{t('status.new_chapters', n=new_count - old_count)}[/success]"
        else:
            entries.append({**base, "current_parts": new_count, "status": "up_to_date", "new_chapters": 0})
            status = f"[muted]{t('status.up_to_date')}[/muted]"
        if not as_json:
            table.add_row(title, str(old_count), str(new_count), status)

    if as_json:
        print(json.dumps(entries, ensure_ascii=False, indent=2))
        return
    console.print(table)
    if any_update:
        console.print(f"[muted]{t('info.updates_available')}[/muted]")


def run_library(args) -> None:
    """Print the library: every story recorded as fully downloaded (mode 1/2),
    which is what --check-updates and --update-library use. With `--json`,
    prints a machine-readable JSON array instead of the table."""
    cli.reset_steps()
    saved = library.load_library()
    if args.json:
        print(json.dumps(
            [{"id": str(story_id), "title": entry.get("title", story_id),
               "num_parts": entry.get("num_parts", 0)}
             for story_id, entry in sorted(saved.items())],
            ensure_ascii=False, indent=2,
        ))
        return
    step_rule(t("step.library"))
    if not saved:
        console.print(f"[muted]{t('info.library_empty')}[/muted]")
        return
    table = Table(box=box.SIMPLE_HEAD, padding=(0, 1), expand=False)
    table.add_column(t("table.title"), style="value")
    table.add_column(t("table.chapters"), style="muted", justify="right")
    table.add_column(t("table.story_id"), style="muted", justify="right")
    for story_id, entry in saved.items():
        table.add_row(entry.get("title", story_id), str(entry.get("num_parts", 0)), str(story_id))
    console.print(table)
    console.print(f"[muted]{t('hint.library_forget')}[/muted]")


def run_library_forget(args) -> None:
    """Remove one story from the library so it stops showing up in
    --library, --check-updates and --update-library."""
    cli.reset_steps()
    try:
        story_id = api.extract_story_id(args.library_forget)
    except ValueError as e:
        console.print(f"[danger]❌  {e}[/danger]")
        sys.exit(1)
    if library.forget_story(story_id):
        console.print(f"[success]{t('ok.removed_from_library', id=story_id)}[/success]")
    else:
        console.print(f"[muted]{t('info.not_in_library', id=story_id)}[/muted]")


def run_info(args) -> None:
    """Show a story's details without downloading anything."""
    cli.reset_steps()
    try:
        story_id = api.extract_story_id(args.id)
    except ValueError as e:
        console.print(f"[danger]❌  {e}[/danger]")
        sys.exit(1)
    title, author, parts, meta = fetch_story_or_exit(story_id, use_cache=not args.no_cache, timeout=args.timeout)
    step_rule(t("step.story_info"))
    table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1), expand=False)
    table.add_column(style="muted")
    table.add_column(style="value")
    table.add_row(t("info.title"), title)
    table.add_row(t("info.author"), author)
    table.add_row(t("info.chapter_count"), str(len(parts)))
    table.add_row(t("info.status"), t("info.status_completed") if meta.get("completed") else t("info.status_ongoing"))
    if meta.get("tags"):
        table.add_row(t("info.genre"), ", ".join(meta["tags"]))
    console.print(Panel(table, border_style="success", box=box.ROUNDED, padding=(1, 2)))
    if meta.get("description"):
        console.print(Panel(
            meta["description"],
            title=f"[muted]{t('info.description')}[/muted]",
            box=box.ROUNDED,
            padding=(1, 2),
        ))


def run_update_library(args) -> None:
    """Re-download every recorded story that has new chapters on Wattpad.

    Every story's file is rewritten in full (the whole document is always written).
    The resume progress is KEPT on success (keep_progress_on_success=True), so
    the next update only fetches the chapters that were added since; the full
    chapter list is still what ends up in the output file.
    """
    cli.reset_steps()
    mode = args.mode or "1"
    saved = library.load_library()
    if not saved:
        console.print(f"[muted]{t('info.library_empty')}[/muted]")
        return
    step_rule(t("step.update_library"))

    up_to_date = []
    to_update = []
    failed = []
    for story_id, entry in saved.items():
        title = entry.get("title", story_id)
        old_count = entry.get("num_parts", 0)
        try:
            title, author, parts, meta = api.get_story_info(story_id, timeout=args.timeout)
        except (api.StoryNotFoundError, api.StoryAccessError, requests.RequestException) as e:
            failed.append((title, str(e)))
            console.print(f"[warning]{t('update.check_failed', title=title, error=e)}[/warning]")
            continue
        new_count = len(parts)
        if new_count > old_count:
            to_update.append((story_id, title, author, parts, meta, old_count, new_count))
        else:
            up_to_date.append(title)

    if not to_update:
        console.print(f"[muted]{t('update.all_up_to_date', n=len(up_to_date), failed=len(failed))}[/muted]")
        return

    config = config_mod.load_config()
    file_format = cli_args.FORMAT_TO_CODE[args.format] if args.format else config.get("file_format", "1")
    if not args.dry_run:
        writers.check_format_libraries(file_format, console)
    save_dir = resolve_save_dir(args.output_dir, config, create_dirs=not args.dry_run)

    console.print(f"[success]{t('update.found', n=len(to_update))}[/success]")
    if args.dry_run:
        for _story_id, title, _author, _parts, _meta, old_count, new_count in to_update:
            console.print(f"[muted]• {title}[/muted] [accent]{old_count} -> {new_count}[/accent]")
        console.print(f"[muted]{t('dryrun.title')}[/muted]")
        return

    for i, (story_id, title, author, parts, meta, old_count, new_count) in enumerate(to_update, start=1):
        console.print(
            f"[primary]{t('update.story_progress', n=i, total=len(to_update), title=title, old=old_count, new=new_count)}[/primary]"
        )
        cli.reset_steps()  # reset the step numbering for every new story
        cover_bytes = fetch_cover(meta, args.no_cover, file_format, timeout=args.timeout)
        run_download(
            story_id, title, author, parts, mode, file_format, save_dir,
            meta=meta, cover_bytes=cover_bytes, skip_existing=args.skip_existing,
            workers=args.workers, include_images=args.include_images, language=args.lang,
            retries=args.retries, timeout=args.timeout,
            keep_progress_on_success=True,
        )
    console.print(f"[success]{t('update.done', n=len(to_update), failed=len(failed))}[/success]")


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


def run_search(args) -> None:
    """Search Wattpad stories with a query string and list them with numbers.

    Without --select: asks which indices to download (like the issue requested),
    plus mode and format, then downloads them. With --select (e.g. "1-8,10" or
    "all"): non-interactive, for scripting; mode/format come from --mode/--format
    or the saved config. Mode is limited to 1 or 2 because picking specific
    chapters makes no sense for several stories at once.

    Results are paged 10 per view. In interactive mode, type "n" for the next
    page and "p" for the previous one; indices are global across all pages,
    so story #13 is always picked with "13" no matter which page is shown.
    """
    cli.reset_steps()
    query = args.search.strip()
    step_rule(t("step.search"))

    try:
        with console.status(f"[accent]{t('status.searching', query=query)}[/accent]", spinner="dots"):
            stories = api.search_stories(query, timeout=args.timeout, limit=args.search_limit)
    except requests.RequestException as e:
        console.print(f"[danger]{t('err.api_access')}[/danger] {e}")
        console.print(f"[muted]{t('hint.check_connection')}[/muted]")
        sys.exit(1)

    if not stories:
        console.print(f"[muted]{t('search.none', query=query)}[/muted]")
        return

    interactive = args.select is None
    page_size = 10
    if interactive:
        page = 0
        max_page = (len(stories) - 1) // page_size
        while True:
            start = page * page_size
            end = min(start + page_size, len(stories))
            if len(stories) > page_size:
                console.print(
                    f"[muted]{t('search.page_info', page=page + 1, total=max_page + 1, start=start + 1, end=end, items=len(stories))}[/muted]"
                )
                console.print(f"[muted]{t('hint.search_page_nav')}[/muted]")
            console.print(_search_table(stories, start, end))
            raw = cli.Prompt.ask(
                f"\n[value]{t('prompt.fanfic_indices')}[/value] [muted]{t('prompt.fanfic_indices_hint')}[/muted]"
            )
            cmd = raw.strip().lower()
            if cmd in ("n", "next"):
                page = min(page + 1, max_page)
                continue
            if cmd in ("p", "prev", "previous"):
                page = max(page - 1, 0)
                continue
            if cmd == "all":
                chosen_indices = list(range(1, len(stories) + 1))
                break
            try:
                chosen_indices = cli.parse_chapter_selection(raw, len(stories))
                break
            except ValueError as e:
                console.print(f"[danger]❌  {e}[/danger]")
        mode = cli.Prompt.ask(
            f"[value]{t('prompt.search_mode')}[/value]",
            choices=["1", "2"],
            default=args.mode or "1",
        )
    else:
        console.print(_search_table(stories, 0, len(stories)))
        if args.select.strip().lower() == "all":
            chosen_indices = list(range(1, len(stories) + 1))
        else:
            try:
                chosen_indices = cli.parse_chapter_selection(args.select, len(stories))
            except ValueError as e:
                console.print(f"[danger]{t('err.select_invalid', error=e)}[/danger]")
                sys.exit(1)
        mode = args.mode or "1"

    console.print(f"[success]{t('ok.stories_selected', n=len(chosen_indices), total=len(stories))}[/success]")

    config = config_mod.load_config()
    if interactive:
        file_format = _ask_file_format(config)
        include_images = _ask_include_images(file_format)
    else:
        file_format = cli_args.FORMAT_TO_CODE[args.format] if args.format else config.get("file_format", "1")
        include_images = args.include_images
    if not args.dry_run:
        writers.check_format_libraries(file_format, console)
    save_dir = resolve_save_dir(args.output_dir, config, create_dirs=not args.dry_run)

    for i, index in enumerate(chosen_indices, start=1):
        story_summary = stories[index - 1]
        console.print(f"[primary]{t('info.story_progress', n=i, total=len(chosen_indices), title=story_summary['title'])}[/primary]")
        cli.reset_steps()  # reset the step numbering for every new story
        title, author, parts, meta = fetch_story_or_exit(
            story_summary["id"], use_cache=not args.no_cache, timeout=args.timeout
        )
        cover_bytes = None if args.dry_run else fetch_cover(meta, args.no_cover, file_format, timeout=args.timeout)
        run_download(
            story_summary["id"], title, author, parts, mode, file_format, save_dir,
            meta=meta, cover_bytes=cover_bytes, skip_existing=args.skip_existing,
            workers=args.workers, include_images=include_images, language=args.lang,
            retries=args.retries, timeout=args.timeout, dry_run=args.dry_run,
        )

    config_mod.save_config(save_dir=str(save_dir), file_format=file_format)


def run_watch(args) -> None:
    """Monitor 1 story continuously (--watch), automatically re-download in full
    as soon as the chapter count increases. Suitable for ongoing stories that update
    regularly. Stop with Ctrl+C, or it stops automatically after
    --watch-max-iterations checks (used for testing, normally not set
    by users so it runs without limit)."""
    cli.reset_steps()
    try:
        cli_args.validate_non_interactive_args(args)
    except ValueError as e:
        console.print(f"[danger]❌  {e}[/danger]")
        sys.exit(1)
    try:
        story_id = api.extract_story_id(args.id)
    except ValueError as e:
        console.print(f"[danger]❌  {e}[/danger]")
        sys.exit(1)

    console.print(f"[value]{t('watch.active', story_id=story_id, interval=args.watch_interval)}[/value]")

    iteration = 0
    last_known_parts = None
    try:
        while True:
            iteration += 1
            try:
                title, author, parts, meta = api.get_story_info(story_id, timeout=args.timeout)
            except (api.StoryNotFoundError, api.StoryAccessError) as e:
                console.print(f"[danger]❌  {e}[/danger]")
                sys.exit(1)
            except requests.RequestException as e:
                console.print(f"[warning]{t('watch.check_failed', iteration=iteration, error=e)}[/warning]")
                parts = None

            if parts is not None and (last_known_parts is None or len(parts) > last_known_parts):
                if last_known_parts is not None:
                    console.print(
                        f"[success]{t('watch.new_chapters', old=last_known_parts, new=len(parts))}[/success]"
                    )
                config = config_mod.load_config()
                file_format = cli_args.FORMAT_TO_CODE[args.format] if args.format else config.get("file_format", "1")
                writers.check_format_libraries(file_format, console)
                save_dir = resolve_save_dir(args.output_dir, config)
                cover_bytes = fetch_cover(meta, args.no_cover, file_format, timeout=args.timeout)
                run_download(
                    story_id, title, author, parts, args.mode, file_format, save_dir,
                    chapters_arg=args.chapters, chapter_arg=args.chapter,
                    meta=meta, cover_bytes=cover_bytes, skip_existing=False,
                    workers=args.workers, include_images=args.include_images, language=args.lang,
                    retries=args.retries, timeout=args.timeout,
                )
                last_known_parts = len(parts)
            elif parts is not None:
                console.print(
                    f"[muted]{t('watch.no_new', n=len(parts), interval=args.watch_interval)}[/muted]"
                )

            if args.watch_max_iterations is not None and iteration >= args.watch_max_iterations:
                console.print(f"[muted]{t('watch.max_reached')}[/muted]")
                break
            time.sleep(args.watch_interval)
    except KeyboardInterrupt:
        console.print(f"[muted]{t('watch.stopped')}[/muted]")


def main():
    args = cli_args.parse_args()  # parse_args also sets the display language (i18n)

    if args.ui_lang:
        # The explicit --ui-lang choice is remembered for the next session.
        config_mod.save_config(ui_lang=args.ui_lang)

    if not args.no_update_check:
        try:
            latest = updater.check_for_update()
            if latest:
                console.print(
                    f"[muted]{t('update.available', latest=latest)}[/muted] "
                    "[accent]pip install --upgrade wattpdl[/accent]\n"
                )
        except Exception:
            pass  # the update check must never stop the main application

    try:
        cli_args.validate_common_args(args)
    except ValueError as e:
        console.print(f"[danger]❌  {e}[/danger]")
        sys.exit(1)

    if args.library:
        run_library(args)
    elif args.library_forget:
        run_library_forget(args)
    elif args.check_updates:
        run_check_updates(args)
    elif args.update_library:
        run_update_library(args)
    elif args.search:
        run_search(args)
    elif args.user:
        run_user_mode(args)
    elif args.id:
        if args.info:
            run_info(args)
        elif args.watch:
            run_watch(args)
        else:
            run_non_interactive(args)
    else:
        run_interactive(args)


if __name__ == "__main__":
    main()
