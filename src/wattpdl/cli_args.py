"""
Command line argument parsing module for non-interactive mode.
If --id/--user is given, the script runs with no prompts at all, which is great for
automation/scripting.
"""
import argparse

from . import __version__, i18n
from . import config as config_mod
from .i18n import SUPPORTED, t

FORMAT_TO_CODE = {"txt": "1", "docx": "2", "epub": "3", "md": "4", "pdf": "5"}


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
    parser.add_argument("--mode", choices=["1", "2", "3", "4"], help=t("help.mode"))
    parser.add_argument(
        "--format", choices=["txt", "docx", "epub", "md", "pdf"],
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
        "--watch", action="store_true",
help=t("help.watch"),
    )
    parser.add_argument(
        "--watch-interval", type=int, default=1800, metavar=t("meta.seconds"),
        help=t("help.watch_interval"),
    )
    parser.add_argument(
        "--watch-max-iterations", type=int, default=None, metavar="N",
        help=argparse.SUPPRESS,  # internal knob for testing, deliberately not documented for users
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
