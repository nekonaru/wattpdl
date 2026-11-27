"""Multi-story flows: --user, --update-library, --search, --file."""
import json
import pathlib
import sys

import requests
from rich import box
from rich.table import Table

from .. import api, cli, cli_args, library, writers
from .. import config as config_mod
from ..cli import console, step_rule
from ..i18n import t
from .common import (
    _search_table,
    fetch_cover,
    from_app,
)


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
    codes = cli_args.resolve_codes(args.format, config.get("file_format", "1"))
    file_format = codes[0]
    if not args.dry_run:
        for code in codes:
            writers.check_format_libraries(code, console)
    save_dir = from_app("resolve_save_dir")(args.output_dir, config, create_dirs=not args.dry_run)

    succeeded, failed = 0, 0
    for n, story_index in enumerate(chosen_indices, start=1):
        story_summary = stories[story_index - 1]
        console.print(f"[primary]{t('info.story_progress', n=n, total=len(chosen_indices), title=story_summary['title'])}[/primary]")
        cli.reset_steps()  # reset the step numbering for every new story, instead of keeping on counting across stories
        info, error = from_app("_fetch_story_tolerant")(story_summary["id"], timeout=args.timeout)
        if info is None:
            failed += 1
            console.print(f"[warning]{t('file.story_failed', id=story_summary['id'], error=error)}[/warning]")
            continue
        title, author, parts, meta = info

        cover_bytes = None if args.dry_run else fetch_cover(meta, args.no_cover, file_format, timeout=args.timeout)

        from_app("run_download")(
            story_summary["id"], title, author, parts, mode, file_format, save_dir,
            meta=meta, cover_bytes=cover_bytes, skip_existing=args.skip_existing,
            workers=args.workers, include_images=args.include_images, language=args.lang,
            retries=args.retries, timeout=args.timeout, dry_run=args.dry_run,
            filename=args.filename, formats=codes, no_library=args.no_library, pdf_pagesize=args.pdf_pagesize, pdf_font_size=args.pdf_font_size,
        )
        succeeded += 1

    console.print(f"[success]{t('file.done', n=succeeded, failed=failed)}[/success]")
    config_mod.save_config(save_dir=str(save_dir), file_format=file_format)

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
    codes = cli_args.resolve_codes(args.format, config.get("file_format", "1"))
    file_format = codes[0]
    if not args.dry_run:
        for code in codes:
            writers.check_format_libraries(code, console)
    save_dir = from_app("resolve_save_dir")(args.output_dir, config, create_dirs=not args.dry_run)

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
        from_app("run_download")(
            story_id, title, author, parts, mode, file_format, save_dir,
            meta=meta, cover_bytes=cover_bytes, skip_existing=args.skip_existing,
            workers=args.workers, include_images=args.include_images, language=args.lang,
            retries=args.retries, timeout=args.timeout,
            keep_progress_on_success=True, formats=codes, no_library=args.no_library, pdf_pagesize=args.pdf_pagesize, pdf_font_size=args.pdf_font_size,
        )
    console.print(f"[success]{t('update.done', n=len(to_update), failed=len(failed))}[/success]")

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
    if not args.json:
        step_rule(t("step.search"))

    try:
        if args.json:
            stories = api.search_stories(query, timeout=args.timeout, limit=args.search_limit)
        else:
            with console.status(f"[accent]{t('status.searching', query=query)}[/accent]", spinner="dots"):
                stories = api.search_stories(query, timeout=args.timeout, limit=args.search_limit)
    except requests.RequestException as e:
        console.print(f"[danger]{t('err.api_access')}[/danger] {e}")
        console.print(f"[muted]{t('hint.check_connection')}[/muted]")
        sys.exit(1)

    if args.search_status:
        wanted = args.search_status == "completed"
        stories = [s for s in stories if s["completed"] == wanted]
    if args.search_min_chapters:
        stories = [s for s in stories if s["num_parts"] >= args.search_min_chapters]
    if args.search_language:
        language = args.search_language.strip().casefold()
        stories = [s for s in stories if language in s["language"].casefold()]
    if args.search_sort == "votes":
        stories.sort(key=lambda s: s["votes"], reverse=True)
    elif args.search_sort == "chapters":
        stories.sort(key=lambda s: s["num_parts"], reverse=True)
    elif args.search_sort == "title":
        stories.sort(key=lambda s: s["title"].casefold())

    if args.json:
        print(json.dumps(stories, ensure_ascii=False, indent=2))
        return

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
        file_format = from_app("_ask_file_format")(config)
        codes = [file_format]
        include_images = from_app("_ask_include_images")(file_format)
    else:
        codes = cli_args.resolve_codes(args.format, config.get("file_format", "1"))
        file_format = codes[0]
        include_images = args.include_images
    if not args.dry_run:
        for code in codes:
            writers.check_format_libraries(code, console)
    save_dir = from_app("resolve_save_dir")(args.output_dir, config, create_dirs=not args.dry_run)

    for i, index in enumerate(chosen_indices, start=1):
        story_summary = stories[index - 1]
        console.print(f"[primary]{t('info.story_progress', n=i, total=len(chosen_indices), title=story_summary['title'])}[/primary]")
        cli.reset_steps()  # reset the step numbering for every new story
        title, author, parts, meta = from_app("fetch_story_or_exit")(
            story_summary["id"], use_cache=not args.no_cache, timeout=args.timeout
        )
        cover_bytes = None if args.dry_run else fetch_cover(meta, args.no_cover, file_format, timeout=args.timeout)
        from_app("run_download")(
            story_summary["id"], title, author, parts, mode, file_format, save_dir,
            meta=meta, cover_bytes=cover_bytes, skip_existing=args.skip_existing,
            workers=args.workers, include_images=include_images, language=args.lang,
            retries=args.retries, timeout=args.timeout, dry_run=args.dry_run,
            formats=codes, no_library=args.no_library, pdf_pagesize=args.pdf_pagesize, pdf_font_size=args.pdf_font_size,
        )

    config_mod.save_config(save_dir=str(save_dir), file_format=file_format)

def run_file_mode(args) -> None:
    """Download the stories listed in a file, one ID or link per line.
    Blank lines and lines starting with '#' are ignored. For each story a full
    download is made (mode 1 or 2); stories that fail to fetch are skipped and
    reported at the end, never aborting the rest of the file."""
    cli.reset_steps()
    step_rule(t("step.file_batch"))
    path = pathlib.Path(args.file)
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as e:
        console.print(f"[danger]{t('err.file_not_found', path=path)}[/danger] {e}")
        sys.exit(1)

    story_ids = []
    for raw in content.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            story_ids.append(api.extract_story_id(line))
        except ValueError:
            console.print(f"[warning]{t('warn.file_bad_line', line=line[:60])}[/warning]")
    if not story_ids:
        console.print(f"[danger]{t('err.file_empty', path=path)}[/danger]")
        sys.exit(1)

    mode = args.mode or "1"
    config = config_mod.load_config()
    codes = cli_args.resolve_codes(args.format, config.get("file_format", "1"))
    file_format = codes[0]
    if not args.dry_run:
        for code in codes:
            writers.check_format_libraries(code, console)
    save_dir = from_app("resolve_save_dir")(args.output_dir, config, create_dirs=not args.dry_run)

    succeeded, failed = 0, 0
    for i, story_id in enumerate(story_ids, start=1):
        console.print(f"[primary]{t('info.story_progress', n=i, total=len(story_ids), title=story_id)}[/primary]")
        cli.reset_steps()  # reset the step numbering for every new story
        info, error = from_app("_fetch_story_tolerant")(story_id, timeout=args.timeout)
        if info is None:
            failed += 1
            console.print(f"[warning]{t('file.story_failed', id=story_id, error=error)}[/warning]")
            continue
        title, author, parts, meta = info
        cover_bytes = None if args.dry_run else fetch_cover(meta, args.no_cover, file_format, timeout=args.timeout)
        from_app("run_download")(
            story_id, title, author, parts, mode, file_format, save_dir,
            meta=meta, cover_bytes=cover_bytes, skip_existing=args.skip_existing,
            workers=args.workers, include_images=args.include_images, language=args.lang,
            retries=args.retries, timeout=args.timeout, dry_run=args.dry_run,
            formats=codes, no_library=args.no_library, pdf_pagesize=args.pdf_pagesize, pdf_font_size=args.pdf_font_size,
        )
        succeeded += 1

    console.print(f"[success]{t('file.done', n=succeeded, failed=failed)}[/success]")
    config_mod.save_config(save_dir=str(save_dir), file_format=file_format)
