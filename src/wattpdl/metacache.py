"""
Short-term story metadata cache module (TTL of a few minutes).

Used so that when the user runs wattpdl several times in a row
for the same story in a short time (e.g. trying out a few
mode/format choices before actually downloading, or an automation script that
calls wattpdl many times for the same story), there is no need to fetch the Wattpad
API again each time; the previous fetch result that is still fresh is enough.

NOT used for long-term purposes (that is the job of the `library` module);
the TTL is deliberately short so story info (chapter count, etc.) stays accurate
if anything does change on Wattpad.
"""
import json
import pathlib
import time

CACHE_DIR = pathlib.Path.home() / ".wattpdl" / "cache"
TTL_SECONDS = 300  # 5 minutes


def _cache_path(story_id: str) -> pathlib.Path:
    return CACHE_DIR / f"{story_id}.json"


def get_cached_story(story_id: str):
    """Return (title, author, parts, meta) from the cache if still fresh
    (TTL_SECONDS not yet passed), None if absent/expired/corrupt."""
    path = _cache_path(story_id)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if time.time() - data.get("cached_at", 0) > TTL_SECONDS:
        return None
    try:
        return data["title"], data["author"], data["parts"], data["meta"]
    except KeyError:
        return None


def save_story_cache(story_id: str, title: str, author: str, parts: list, meta: dict) -> None:
    """Save the story info fetch result to the cache. A write failure (disk full,
    no permission, etc.) must not disturb the main flow; the cache is only an
    optimization, not an essential part."""
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        _cache_path(story_id).write_text(
            json.dumps(
                {"cached_at": time.time(), "title": title, "author": author, "parts": parts, "meta": meta},
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
    except OSError:
        pass
