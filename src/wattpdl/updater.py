"""
Modul cek update: bandingkan versi wattpdl yang terinstall dengan versi
terbaru di PyPI. Hasilnya di-cache di disk supaya tidak mengecek ke PyPI
tiap kali aplikasi dijalankan — cukup sekali per CHECK_INTERVAL.

Prinsip penting: kegagalan cek update (tidak ada internet, PyPI down, dll)
TIDAK BOLEH pernah mengganggu jalannya aplikasi utama. Semua fungsi di sini
menelan error-nya sendiri dan mengembalikan None kalau gagal.
"""
import json
import pathlib
import time

import requests

from . import __version__

PYPI_URL = "https://pypi.org/pypi/wattpdl/json"
CACHE_FILE = pathlib.Path.home() / ".wattpdl" / "update_check.json"
CHECK_INTERVAL = 24 * 3600  # cek ulang ke PyPI maksimal sekali sehari


def _parse_version(v: str) -> tuple:
    """Ubah string versi ('1.10.2') jadi tuple angka (1, 10, 2) supaya bisa
    dibandingkan urutannya dengan benar (bukan perbandingan string, yang salah
    untuk kasus semacam '1.9' vs '1.10')."""
    parts = []
    for p in (v or "").split("."):
        digits = "".join(ch for ch in p if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def _load_cache() -> dict:
    if not CACHE_FILE.exists():
        return {}
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_cache(data: dict) -> None:
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(json.dumps(data), encoding="utf-8")
    except OSError:
        pass


def check_for_update(force: bool = False):
    """
    Kembalikan string versi terbaru kalau ada versi PyPI yang lebih baru dari
    yang terinstall, None kalau sudah paling baru / gagal cek / masih dalam
    interval cache. Tidak pernah raise exception.
    """
    cache = _load_cache()
    now = time.time()
    if not force and cache.get("checked_at") and now - cache["checked_at"] < CHECK_INTERVAL:
        latest = cache.get("latest_version")
    else:
        try:
            resp = requests.get(PYPI_URL, timeout=5)
            resp.raise_for_status()
            latest = resp.json().get("info", {}).get("version")
        except Exception:
            return None
        _save_cache({"checked_at": now, "latest_version": latest})

    if not latest:
        return None
    if _parse_version(latest) > _parse_version(__version__):
        return latest
    return None
