"""
"Library" module, which records stories that were fully downloaded (all
chapters, via mode 1/2), along with the chapter count at that time. Used
by the `--check-updates` feature: compare the chapter count recorded
here with the current chapter count on Wattpad, so the user knows which
ongoing stories have new chapters without opening them one by one.

Deliberately separate from `progress` (which handles resuming a download that is
running/stopped) and `metacache` (a short-term cache of a few minutes);
the data here is meant to last a long time (until the user downloads that story again).
"""
import json
import pathlib

LIBRARY_FILE = pathlib.Path.home() / ".wattpdl" / "library.json"


def load_library() -> dict:
    """Return every recorded story: {story_id: {"title", "num_parts"}}."""
    if not LIBRARY_FILE.exists():
        return {}
    try:
        return json.loads(LIBRARY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def remember_story(story_id: str, title: str, num_parts: int) -> None:
    """Record/update 1 story in the library, called after that story was
    fully downloaded (mode 1/2, with no failed chapters)."""
    library = load_library()
    library[str(story_id)] = {"title": title, "num_parts": num_parts}
    try:
        LIBRARY_FILE.parent.mkdir(parents=True, exist_ok=True)
        LIBRARY_FILE.write_text(json.dumps(library, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass
