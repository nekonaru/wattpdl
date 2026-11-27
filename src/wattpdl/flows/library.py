"""Library, check-updates, author info and history flows."""
import json
import sys

import requests
from rich import box
from rich.table import Table

from .. import api, cli, library
from ..cli import console, step_rule
from ..i18n import t


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

def run_author_info(args) -> None:
    """List an author's published stories with totals, without downloading."""
    cli.reset_steps()
    try:
        if args.json:
            stories = api.get_author_stories(args.author_info, timeout=args.timeout)
        else:
            with console.status(f"[accent]{t('status.fetching_user_stories', user=args.author_info)}[/accent]",
                                spinner="dots"):
                stories = api.get_author_stories(args.author_info, timeout=args.timeout)
    except (api.StoryNotFoundError, api.StoryAccessError) as e:
        console.print(f"[danger]{t('err.no_user_stories', user=args.author_info)}[/danger] {e}")
        sys.exit(1)
    except requests.RequestException as e:
        console.print(f"[danger]{t('err.api_access')}[/danger] {e}")
        sys.exit(1)
    if args.json:
        print(json.dumps(stories, ensure_ascii=False, indent=2))
        return
    if not stories:
        console.print(f"[danger]{t('err.no_user_stories', user=args.author_info)}[/danger]")
        return
    table = Table(box=box.SIMPLE_HEAD, padding=(0, 1), expand=False)
    table.add_column(t("table.no"), style="muted", justify="right", width=5)
    table.add_column(t("table.title"), style="value")
    table.add_column(t("table.chapters"), style="muted", justify="right")
    table.add_column(t("table.status"), style="muted")
    for i, story in enumerate(stories, start=1):
        table.add_row(str(i), story["title"], str(story["num_parts"]),
                      t("info.status_completed") if story["completed"] else t("info.status_ongoing"))
    console.print(table)
    console.print(f"[muted]{t('author.summary', n=len(stories), chapters=sum(s['num_parts'] for s in stories))}[/muted]")

def run_history(args) -> None:
    """Show the local download history (or JSON with --json)."""
    cli.reset_steps()
    entries = library.load_history()
    if args.json:
        print(json.dumps(entries, ensure_ascii=False, indent=2))
        return
    if not entries:
        console.print(f"[muted]{t('history.empty')}[/muted]")
        return
    table = Table(box=box.SIMPLE_HEAD, padding=(0, 1), expand=False)
    table.add_column(t("table.title"), style="value")
    table.add_column(t("table.chapters"), style="muted", justify="right")
    table.add_column(t("config.value"), style="muted")
    table.add_column(t("history.at"), style="muted")
    for entry in entries[:50]:
        table.add_row(entry.get("title", "?"), str(entry.get("chapters", 0)),
                      ", ".join(entry.get("formats", [])), str(entry.get("at", "")))
    console.print(table)
