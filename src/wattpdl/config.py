"""
User configuration module: saves preferences (last save folder & file
format) so they do not need to be filled in again every time the script runs.
Stored in ~/.wattpdl/config.json.
"""
import json
import pathlib

CONFIG_DIR = pathlib.Path.home() / ".wattpdl"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "version": 2,         # schema version (migrated automatically when loading older files)
    "save_dir": None,     # last save folder path, None = use the Downloads folder
    "file_format": "1",   # "1" = .txt, "2" = .docx, "3" = .epub, "4" = .md, "5" = .pdf
    "ui_lang": None,      # CLI display language: "id" / "en", None = follow the default (en)
}


def load_config() -> dict:
    """Read the config from disk. Return the defaults if it does not exist yet / its content is corrupt."""
    if not CONFIG_FILE.exists():
        return dict(DEFAULT_CONFIG)
    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return dict(DEFAULT_CONFIG)
    if not isinstance(data, dict):
        return dict(DEFAULT_CONFIG)

    merged = dict(DEFAULT_CONFIG)
    merged.update({k: v for k, v in data.items() if k in DEFAULT_CONFIG})
    merged["version"] = 2  # migrate old files (no version or version 1) automatically
    if merged.get("file_format") not in ("1", "2", "3", "4", "5"):
        merged["file_format"] = DEFAULT_CONFIG["file_format"]
    return merged


def save_config(**updates) -> None:
    """Save/merge new preferences into the on-disk config."""
    config = load_config()
    config.update(updates)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding="utf-8")
