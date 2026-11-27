"""Interactive, non-interactive, info and watch flows."""
import json
import pathlib
import sys
import time

import requests
from rich import box
from rich.align import Align
from rich.panel import Panel
from rich.table import Table

from .. import api, cli, cli_args, writers
from .. import config as config_mod
from ..cli import console, step_rule
from ..i18n import t
from .common import (
    fetch_cover,
    from_app,
    print_story_info,
)


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
    title, author, parts, meta = from_app("fetch_story_or_exit")(story_id, use_cache=not args.no_cache, timeout=args.timeout)

    step_rule(t("step.story_info"))
    print_story_info(title, author, parts)

    codes = cli_args.resolve_codes(args.format, config.get("file_format", "1"))
    file_format = codes[0]
    if not args.dry_run:
        for code in codes:
            writers.check_format_libraries(code, console)

    save_dir = from_app("resolve_save_dir")(args.output_dir, config, create_dirs=not args.dry_run)

    cover_bytes = None if args.dry_run else fetch_cover(meta, args.no_cover, file_format, timeout=args.timeout)

    from_app("run_download")(
        story_id, title, author, parts, args.mode, file_format, save_dir,
        chapters_arg=args.chapters, chapter_arg=args.chapter,
        meta=meta, cover_bytes=cover_bytes, skip_existing=args.skip_existing,
        workers=args.workers, include_images=args.include_images, language=args.lang,
        retries=args.retries, timeout=args.timeout, dry_run=args.dry_run,
        filename=args.filename, formats=codes, no_library=args.no_library, pdf_pagesize=args.pdf_pagesize, pdf_font_size=args.pdf_font_size,
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

    title, author, parts, meta = from_app("fetch_story_or_exit")(story_id, timeout=timeout)

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

    file_format = from_app("_ask_file_format")(config)
    codes = [file_format]
    if not dry_run:
        for code in codes:
            writers.check_format_libraries(code, console)

    include_images = from_app("_ask_include_images")(file_format)

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
    save_dir = from_app("resolve_save_dir")(custom or (args.output_dir if args else ""), config, create_dirs=not dry_run)

    # Fetched after every question was answered: a silent network wait between
    # prompts makes people press Enter again, which then answers the next prompts.
    cover_bytes = None if dry_run else fetch_cover(meta, False, file_format, timeout=timeout)

    from_app("run_download")(story_id, title, author, parts, mode, file_format, save_dir,
                 meta=meta, cover_bytes=cover_bytes, interactive=True,
                 workers=workers, include_images=include_images,
                 retries=retries, timeout=timeout, dry_run=dry_run,
                 filename=args.filename if args else None, no_library=args.no_library, pdf_pagesize=args.pdf_pagesize, pdf_font_size=args.pdf_font_size)

def run_info(args) -> None:
    """Show a story's details without downloading anything."""
    cli.reset_steps()
    try:
        story_id = api.extract_story_id(args.id)
    except ValueError as e:
        console.print(f"[danger]❌  {e}[/danger]")
        sys.exit(1)
    title, author, parts, meta = from_app("fetch_story_or_exit")(story_id, use_cache=not args.no_cache, timeout=args.timeout)
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
                    if args.watch_notify_json:
                        print(json.dumps({"story_id": str(story_id), "old": last_known_parts,
                                          "new": len(parts), "new_chapters": len(parts) - last_known_parts},
                                         ensure_ascii=False))
                config = config_mod.load_config()
                codes = cli_args.resolve_codes(args.format, config.get("file_format", "1"))
                file_format = codes[0]
                for code in codes:
                    writers.check_format_libraries(code, console)
                save_dir = from_app("resolve_save_dir")(args.output_dir, config)
                cover_bytes = fetch_cover(meta, args.no_cover, file_format, timeout=args.timeout)
                from_app("run_download")(
                    story_id, title, author, parts, args.mode, file_format, save_dir,
                    chapters_arg=args.chapters, chapter_arg=args.chapter,
                    meta=meta, cover_bytes=cover_bytes, skip_existing=False,
                    workers=args.workers, include_images=args.include_images, language=args.lang,
                    retries=args.retries, timeout=args.timeout, formats=codes, no_library=args.no_library, pdf_pagesize=args.pdf_pagesize, pdf_font_size=args.pdf_font_size,
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
