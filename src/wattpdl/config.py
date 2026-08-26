"""
Modul konfigurasi user: menyimpan preferensi (folder simpan & format file
terakhir) supaya tidak perlu diisi ulang tiap kali menjalankan script.
Disimpan di ~/.wattpdl/config.json.
"""
import json
import pathlib

CONFIG_DIR = pathlib.Path.home() / ".wattpdl"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "save_dir": None,     # path folder simpan terakhir, None = pakai folder Downloads
    "file_format": "1",   # "1" = .txt, "2" = .docx, "3" = .epub, "4" = .md
}


def load_config() -> dict:
    """Baca config dari disk. Kembalikan default kalau belum ada / isinya rusak."""
    if not CONFIG_FILE.exists():
        return dict(DEFAULT_CONFIG)
    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_CONFIG)

    merged = dict(DEFAULT_CONFIG)
    merged.update({k: v for k, v in data.items() if k in DEFAULT_CONFIG})
    return merged


def save_config(**updates) -> None:
    """Simpan/gabungkan preferensi baru ke config di disk."""
    config = load_config()
    config.update(updates)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding="utf-8")
