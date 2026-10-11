"""
Update check module: compare the installed wattpdl version with the latest
version on PyPI. The result is cached on disk so PyPI is not checked
every time the app runs, only once per CHECK_INTERVAL.

Important principle: a failed update check (no internet, PyPI down, etc.)
must NEVER disturb the main application. Every function here
swallows its own errors and returns None on failure.
"""
import json
import pathlib
import time

import requests

from . import __version__

PYPI_URL = "https://pypi.org/pypi/wattpdl/json"
CACHE_FILE = pathlib.Path.home() / ".wattpdl" / "update_check.json"
CHECK_INTERVAL = 24 * 3600  # re-check PyPI at most once a day


def _parse_version(v: str) -> tuple:
    """Turn a version string ('1.10.2') into a tuple of numbers (1, 10, 2) so the order
    can be compared correctly (not a string comparison, which is wrong
    for cases such as '1.9' vs '1.10')."""
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
    Return the latest version string if a PyPI version newer than the
    installed one exists, None if already the latest / the check failed / still within the
    cache interval. Never raises an exception.
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
