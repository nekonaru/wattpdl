"""WattPDL: Wattpad Story Downloader.

Public facade: imports all CLI flows from `flows/` and dispatches from `main()`.
"""
import pathlib  # noqa: F401  (public facade for tests and extensions)
import sys
import time  # noqa: F401

from . import api, cli, cli_args, library, metacache, updater, writers  # noqa: F401
from . import config as config_mod
from . import progress as progress_mod  # noqa: F401
from .cli import console, step_rule  # noqa: F401
from .flows.batch import run_file_mode, run_search, run_update_library, run_user_mode
from .flows.common import (
    REPORT_ENTRIES,
    _ask_file_format,
    _ask_include_images,
    _fetch_story_tolerant,
    _output_base_name,
    _output_path,
    _search_table,
    _write_output,
    fetch_cover,
    fetch_story_or_exit,
    print_story_info,
    resolve_chapters,
    resolve_save_dir,
    should_skip_existing,
    warn_if_parts_missing,
    write_report,  # noqa: F401  (public facade)
)
from .flows.download import run_download
from .flows.library import run_author_info, run_check_updates, run_history, run_library, run_library_forget
from .flows.single import run_info, run_interactive, run_non_interactive, run_watch
from .flows.tooling import completion_script, doctor_checks, run_config_commands, run_doctor
from .i18n import t  # noqa: F401

__all__ = [
    "main", "api", "cli", "cli_args", "library", "metacache", "updater", "writers",
    "config_mod", "progress_mod", "console", "step_rule", "t", "pathlib", "time",
    "REPORT_ENTRIES", "write_report",
    "_ask_file_format", "_ask_include_images", "_fetch_story_tolerant",
    "_output_base_name", "_output_path", "_search_table", "_write_output",
    "fetch_cover", "fetch_story_or_exit", "print_story_info", "resolve_chapters",
    "resolve_save_dir", "should_skip_existing", "warn_if_parts_missing",
    "run_download", "run_non_interactive", "run_interactive", "run_info", "run_watch",
    "run_user_mode", "run_update_library", "run_search", "run_file_mode",
    "run_check_updates", "run_library", "run_library_forget", "run_author_info",
    "run_history", "completion_script", "doctor_checks", "run_config_commands", "run_doctor",
]


def main():
    args = cli_args.parse_args()  # parse_args also sets the display language (i18n)
    cli.set_verbosity(quiet=args.quiet, verbose=args.verbose)
    REPORT_ENTRIES.clear()

    if args.completion:
        print(completion_script(args.completion))
        return
    if args.doctor:
        run_doctor()
        return
    if args.author_info:
        run_author_info(args)
        return
    if args.history:
        run_history(args)
        return
    if args.config or args.config_set:
        run_config_commands(args)
        return

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

    if cli.VERBOSE:
        console.print(f"[muted]verbose: mode={args.mode or 'default'}, format={args.format or 'default'}, "
                      f"workers={args.workers}, retries={args.retries}, timeout={args.timeout}[/muted]")

    if args.library:
        run_library(args)
    elif args.library_forget:
        run_library_forget(args)
    elif args.check_updates:
        run_check_updates(args)
    elif args.update_library:
        run_update_library(args)
    elif args.file:
        run_file_mode(args)
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

    if args.report and REPORT_ENTRIES:
        write_report(args.report)
        console.print(f"[muted]{t('report.written', path=args.report)}[/muted]")


if __name__ == "__main__":
    main()
