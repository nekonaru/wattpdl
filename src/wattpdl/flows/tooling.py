"""Shell completion, preference commands and the doctor self-check."""
import importlib
import pathlib
import platform
import sys

from rich import box
from rich.panel import Panel
from rich.table import Table

from .. import api, cli_args, library, metacache
from .. import config as config_mod
from .. import progress as progress_mod
from ..cli import console
from ..i18n import t
from .common import from_app


def completion_script(shell: str) -> str:
    """Print a small shell-completion script for wattpdl's own flags."""
    options = []
    for action in cli_args.build_parser()._actions:
        for opt in getattr(action, "option_strings", []):
            if opt.startswith("--") and opt not in options:
                options.append(opt)
    words = " ".join(options)
    if shell == "bash":
        return (
            "_wattpdl_completion() {\n"
            '    local cur="${COMP_WORDS[COMP_CWORD]}"\n'
            f'    COMPREPLY=( $(compgen -W "{words}" -- "$cur") )\n'
            "}\n"
            "complete -F _wattpdl_completion wattpdl\n"
        )
    if shell == "zsh":
        return (
            "#compdef wattpdl\n"
            "_wattpdl() {\n"
            f"    compadd -- {words}\n"
            "}\n"
            "compdef _wattpdl wattpdl\n"
        )
    if shell == "fish":
        return "\n".join(f"complete -c wattpdl -l {opt[2:]}" for opt in options) + "\n"
    return (
        "Register-ArgumentCompleter -Native -CommandName wattpdl -ScriptBlock {\n"
        "    param($wordToComplete)\n"
        f"    @({', '.join(repr(opt) for opt in options)}) |"
        " Where-Object { $_ -like \"$wordToComplete*\" }\n"
        "}\n"
    )


def run_config_commands(args) -> None:
    """--config shows the saved preferences; --config-set updates them."""
    updates = cli_args.parse_config_set(args.config_set)
    if updates:
        config_mod.save_config(**updates)
        for key, value in updates.items():
            console.print(f"[success]{t('config.updated', name=key, value=value)}[/success]")
    if args.config or not updates:
        config = config_mod.load_config()
        table = Table(box=box.SIMPLE_HEAD, padding=(0, 1), expand=False)
        table.add_column(t("config.key"), style="value")
        table.add_column(t("config.value"), style="muted")
        for key, value in config.items():
            table.add_row(key, str(value))
        console.print(Panel(table, title=f"[primary]{t('config.title')}[/primary]",
                            box=box.ROUNDED, padding=(1, 2)))


def doctor_checks() -> list:
    """Run the self-diagnostic checks and return (name, ok, detail) rows."""

    rows = []
    py_ok = sys.version_info >= (3, 10)
    rows.append((t("doctor.python"), py_ok, platform.python_version()))
    modules = ("requests", "rich", "docx", "ebooklib", "reportlab", "PIL")
    found = []
    for module in modules:
        try:
            importlib.import_module(module)
            found.append(module)
        except ImportError:
            pass
    rows.append((t("doctor.deps"), len(found) == len(modules), ", ".join(found)))
    try:
        config = config_mod.load_config()
        rows.append((t("doctor.config"), True, f"file_format={config['file_format']}, ui_lang={config['ui_lang']}"))
    except Exception as e:
        rows.append((t("doctor.config"), False, str(e)))
    dirs = (config_mod.CONFIG_DIR, metacache.CACHE_DIR, progress_mod.PROGRESS_DIR,
            library.LIBRARY_FILE.parent)
    dir_ok, dir_detail = True, []
    for path in dirs:
        try:
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)
            dir_detail.append(str(path))
        except OSError as e:
            dir_ok = False
            dir_detail.append(f"{path}: {e}")
    rows.append((t("doctor.dirs"), dir_ok, " | ".join(dir_detail)))
    try:
        _title, _author, parts, _meta = api.get_story_info("398440633", timeout=5)
        rows.append((t("doctor.api"), bool(parts), f"{len(parts)} chapters"))
    except Exception as e:
        rows.append((t("doctor.api"), False, str(e)))
    return rows


def run_doctor() -> None:
    table = Table(box=box.SIMPLE_HEAD, padding=(0, 1), expand=False)
    table.add_column(t("config.key"), style="value")
    table.add_column(t("doctor.title"), style="muted")
    table.add_column(t("config.value"), style="muted")
    for name, ok, detail in from_app("doctor_checks")():
        table.add_row(name, t("doctor.ok") if ok else t("doctor.fail"), str(detail)[:100])
    console.print(Panel(table, title=f"[primary]{t('doctor.title')}[/primary]",
                        box=box.ROUNDED, padding=(1, 2)))
