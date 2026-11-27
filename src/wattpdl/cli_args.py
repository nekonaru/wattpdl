"""
Command line argument parsing module for non-interactive mode.
If --id/--user is given, the script runs with no prompts at all, which is great for
automation/scripting.
"""
import argparse
import pathlib
import re

from . import __version__, i18n
from . import config as config_mod
from .i18n import SUPPORTED, t

FORMAT_TO_CODE = {"txt": "1", "docx": "2", "epub": "3", "md": "4", "pdf": "5"}
FORMATS = tuple(FORMAT_TO_CODE)


def parse_formats(value) -> list:
    """Parse `--format`: a single format, a comma-separated list, or `all`."""
    if not value:
        return []
    parts = [part.strip().lower() for part in str(value).split(",") if part.strip()]
    if not parts:
        raise ValueError(t("val.format_invalid", value=value))
    if "all" in parts:
        return list(FORMATS)
    invalid = [part for part in parts if part not in FORMATS]
    if invalid:
        raise ValueError(t("val.format_invalid", value=", ".join(invalid)))
    return list(dict.fromkeys(parts))


CONFIG_KEYS = ("save_dir", "file_format", "ui_lang")


def resolve_codes(format_arg, default_code) -> list:
    """Format codes to write: from `--format` (single, list or `all`), or the saved default."""
    formats = parse_formats(format_arg)
    if formats:
        return [FORMAT_TO_CODE[fmt] for fmt in formats]
    return [default_code]


def parse_config_set(items) -> dict:
    """Parse `--config-set key=value` items and validate keys/values."""
    updates = {}
    for item in items or []:
        if "=" not in item:
            raise ValueError(t("val.config_set_format", item=item))
        key, value = item.split("=", 1)
        key, value = key.strip(), value.strip()
        if key not in CONFIG_KEYS:
            raise ValueError(t("val.config_set_key", name=key))
        if key == "file_format":
            value = FORMAT_TO_CODE.get(value, value)
            if value not in FORMAT_TO_CODE.values():
                raise ValueError(t("val.config_set_value", name=key, value=value))
        elif key == "ui_lang" and value not in SUPPORTED:
            raise ValueError(t("val.config_set_value", name=key, value=value))
        updates[key] = value
    return updates


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wattpdl",
        description=t("help.description"),
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--id", metavar=t("meta.id"),
        help=t("help.id"),
    )
    parser.add_argument(
        "--mode", choices=["1", "2", "3", "4"],
        help=t("help.mode"),
    )
    parser.add_argument(
        "--format", metavar="txt|docx|epub|md|pdf|all",
        help=t("help.format"),
    )
    parser.add_argument(
        "--chapters", metavar="1,3,5-8",
        help=t("help.chapters"),
    )
    parser.add_argument(
        "--chapter", type=int, metavar="N",
        help=t("help.chapter"),
    )
    parser.add_argument(
        "--output-dir", metavar="PATH",
        help=t("help.output_dir"),
    )
    parser.add_argument(
        "--skip-existing", action="store_true",
        help=t("help.skip_existing"),
    )
    parser.add_argument(
        "--no-cover", action="store_true",
        help=t("help.no_cover"),
    )
    parser.add_argument(
        "--include-images", action="store_true",
        help=t("help.include_images"),
    )
    parser.add_argument(
        "--workers", type=int, default=1, metavar="N",
        help=t("help.workers"),
    )
    parser.add_argument(
        "--no-cache", action="store_true",
        help=t("help.no_cache"),
    )
    parser.add_argument(
        "--lang", metavar=t("meta.code"), default="id",
        help=t("help.lang"),
    )
    parser.add_argument(
        "--ui-lang", choices=list(SUPPORTED), metavar="id|en", default=None,
        help=t("help.ui_lang"),
    )
    parser.add_argument(
        "--no-update-check", action="store_true",
        help=t("help.no_update_check"),
    )

    # --- download all/selected stories from 1 author ---
    parser.add_argument(
        "--user", metavar="USERNAME",
        help=t("help.user"),
    )
    parser.add_argument(
        "--user-select", metavar="all|1,3,5", default="all",
        help=t("help.user_select"),
    )

    # --- detect new chapters for stories that were downloaded before ---
    parser.add_argument(
        "--check-updates", action="store_true",
        help=t("help.check_updates"),
    )

    # --- watch mode: monitor an ongoing story, auto re-download when there are new chapters ---
    parser.add_argument(
        "--file", metavar="PATH",
        help=t("help.file"),
    )
    parser.add_argument(
        "--filename", metavar="NAME",
        help=t("help.filename"),
    )
    parser.add_argument(
        "--watch", action="store_true",
        help=t("help.watch"),
    )
    parser.add_argument(
        "--watch-interval", type=int, default=1800, metavar=t("meta.seconds"),
        help=t("help.watch_interval"),
    )
    parser.add_argument(
        "--watch-notify-json", action="store_true",
        help=t("help.watch_notify_json"),
    )
    parser.add_argument(
        "--watch-max-iterations", type=int, default=None, metavar="N",
        help=t("help.watch_max_iterations"),
    )

    # --- search Wattpad and download several stories at once ---
    parser.add_argument(
        "--search", metavar="QUERY",
        help=t("help.search"),
    )
    parser.add_argument(
        "--search-limit", type=int, default=40, metavar="N",
        help=t("help.search_limit"),
    )
    parser.add_argument(
        "--search-status", choices=["completed", "ongoing"],
        help=t("help.search_status"),
    )
    parser.add_argument(
        "--search-min-chapters", type=int, default=0, metavar="N",
        help=t("help.search_min_chapters"),
    )
    parser.add_argument(
        "--search-sort", choices=["votes", "chapters", "title"],
        help=t("help.search_sort"),
    )
    parser.add_argument(
        "--search-language", metavar="NAME",
        help=t("help.search_language"),
    )
    parser.add_argument(
        "--select", metavar="all|1,3,5-8",
        help=t("help.select"),
    )

    # --- manage the local library of stories to keep up to date ---
    parser.add_argument(
        "--library", action="store_true",
        help=t("help.library"),
    )
    parser.add_argument(
        "--library-forget", metavar=t("meta.id"),
        help=t("help.library_forget"),
    )
    parser.add_argument(
        "--update-library", action="store_true",
        help=t("help.update_library"),
    )
    parser.add_argument(
        "--json", action="store_true",
        help=t("help.json"),
    )
    parser.add_argument(
        "--info", action="store_true",
        help=t("help.info"),
    )

    # --- HTTP tuning ---
    parser.add_argument(
        "--retries", type=int, default=3, metavar="N",
        help=t("help.retries"),
    )
    parser.add_argument(
        "--timeout", type=int, default=20, metavar="N",
        help=t("help.timeout"),
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help=t("help.dry_run"),
    )
    parser.add_argument(
        "--report", metavar="PATH",
        help=t("help.report"),
    )
    parser.add_argument(
        "--author-info", metavar="USERNAME",
        help=t("help.author_info"),
    )
    parser.add_argument(
        "--history", action="store_true",
        help=t("help.history"),
    )
    parser.add_argument(
        "--no-library", action="store_true",
        help=t("help.no_library"),
    )
    parser.add_argument(
        "--pdf-pagesize", choices=["A4", "A5"], default="A5",
        help=t("help.pdf_pagesize"),
    )
    parser.add_argument(
        "--pdf-font-size", type=int, default=10, metavar="N",
        help=t("help.pdf_font_size"),
    )

    # --- tooling and preferences ---
    parser.add_argument(
        "--config", action="store_true",
        help=t("help.config"),
    )
    parser.add_argument(
        "--config-set", action="append", default=[], metavar="KEY=VALUE",
        help=t("help.config_set"),
    )
    parser.add_argument(
        "--doctor", action="store_true",
        help=t("help.doctor"),
    )
    parser.add_argument(
        "--completion", choices=["bash", "zsh", "fish", "powershell"],
        help=t("help.completion"),
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help=t("help.quiet"),
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help=t("help.verbose"),
    )

    return parser


def _apply_ui_language(argv=None) -> str:
    """Determine & activate the display language BEFORE the parser is built, because the --help text
    and argparse error messages are created when the parser is built. Priority: --ui-lang >
    env WATTPDL_LANG > saved config > default (en)."""
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--ui-lang", default=None)
    known, _ = pre.parse_known_args(argv)
    lang = i18n.resolve_language(known.ui_lang, config_mod.load_config().get("ui_lang"))
    return i18n.set_language(lang)


def parse_args(argv=None) -> argparse.Namespace:
    _apply_ui_language(argv)
    return build_parser().parse_args(argv)


def validate_common_args(args: argparse.Namespace) -> None:
    """Validate the argument combinations that apply to every mode.
    Raise ValueError with a clear message on misuse."""
    if args.retries < 1:
        raise ValueError(t("val.retries_min"))
    if args.retries > 10:
        raise ValueError(t("val.retries_max"))
    parse_formats(args.format)
    parse_config_set(args.config_set)
    if args.report and pathlib.Path(args.report).suffix.lower() not in (".json", ".csv"):
        raise ValueError(t("val.report_ext"))
    if args.search_min_chapters < 0:
        raise ValueError(t("val.search_min_chapters"))
    if not 6 <= args.pdf_font_size <= 24:
        raise ValueError(t("val.pdf_font_size"))
    if args.watch_max_iterations is not None and args.watch_max_iterations < 1:
        raise ValueError(t("val.watch_iterations"))
    if (args.search_status or args.search_sort or args.search_language or args.search_min_chapters > 0) \
            and not args.search:
        raise ValueError(t("val.filters_require_search"))
    if args.timeout < 1:
        raise ValueError(t("val.timeout_min"))
    if args.search_limit < 1 or args.search_limit > 100:
        raise ValueError(t("val.search_limit_bounds"))
    if args.watch_interval < 1:
        raise ValueError(t("val.watch_interval_min"))
    standalone = [args.library, bool(args.library_forget), args.update_library, bool(args.search),
                  bool(args.file), args.doctor, bool(args.completion), args.config, bool(args.config_set),
                  bool(args.author_info), args.history]
    if args.json and not (args.library or args.check_updates or args.search):
        raise ValueError(t("val.json_requires"))
    if any(standalone) and (args.id or args.user):
        raise ValueError(t("val.standalone_conflict"))
    if args.select is not None and not args.search:
        raise ValueError(t("val.select_requires_search"))
    if args.search is not None and not args.search.strip():
        raise ValueError(t("val.search_empty"))
    if args.search is not None and args.mode is not None and args.mode not in ("1", "2"):
        raise ValueError(t("val.search_mode"))
    if args.file and args.mode is not None and args.mode not in ("1", "2"):
        raise ValueError(t("val.file_mode"))
    if args.filename and not args.id:
        raise ValueError(t("val.filename_requires_id"))
    if args.info and not args.id:
        raise ValueError(t("val.info_requires_id"))
    if args.update_library and args.mode is not None and args.mode not in ("1", "2"):
        raise ValueError(t("val.update_library_mode"))
    if args.user is not None and not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", args.user.strip()):
        raise ValueError(t("val.username_invalid", user=args.user.strip()))


def validate_non_interactive_args(args: argparse.Namespace) -> None:
    """
    Validate the argument combination for non-interactive mode (used after --id is given).
    Raise ValueError with a clear message if a required argument is missing.
    """
    if not args.mode:
        raise ValueError(t("val.mode_required"))
    if args.mode == "3" and not args.chapters:
        raise ValueError(t("val.chapters_required"))
    if args.mode == "4" and args.chapter is None:
        raise ValueError(t("val.chapter_required"))
    if args.workers < 1:
        raise ValueError(t("val.workers_min"))
