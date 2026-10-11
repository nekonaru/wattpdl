"""
Resume/progress module: saves the chapters that were already downloaded successfully for
a story, so that if the process stops midway (hangs, connection
lost, terminal closed), running again with the same story will
continue from the last successful chapter instead of starting over.

Stored per story in ~/.wattpdl/progress/<story_id>.json
"""
import json
import pathlib
import threading

PROGRESS_DIR = pathlib.Path.home() / ".wattpdl" / "progress"


def _progress_path(story_id: str) -> pathlib.Path:
    return PROGRESS_DIR / f"{story_id}.json"


def load_progress(story_id: str) -> dict:
    """
    Return the chapters already saved for this story:
    {part_id (str): {"title": ..., "text": ...}}
    Empty if there has never been any progress or the file is corrupt.
    """
    path = _progress_path(story_id)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_chapter_progress(story_id: str, part_id, title: str, text: str) -> None:
    """Save one chapter that was just downloaded successfully to this story's progress file.

    Kept as a standalone function for compatibility & simple use
    (read-modify-write once). For a session that downloads many chapters
    in a row, use `ProgressStore` below: it reads the file only once
    at the start and then keeps the state in memory, so the whole
    JSON does not need to be re-read each time 1 chapter finishes (O(n) per save, instead of O(n) read + O(n) write
    repeated for every chapter = O(n^2) total for a long story).
    """
    data = load_progress(story_id)
    data[str(part_id)] = {"title": title, "text": text}
    PROGRESS_DIR.mkdir(parents=True, exist_ok=True)
    _progress_path(story_id).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def clear_progress(story_id: str) -> None:
    """Delete this story's progress file (called after all chapters were downloaded successfully)."""
    path = _progress_path(story_id)
    if path.exists():
        path.unlink()


class ProgressStore:
    """Hold one story's progress in memory for the duration of one download session.

    Used by `cli.download_chapters()` so each chapter that finishes
    downloading only needs to update the dict in memory + write to disk once (without
    re-reading the file from the start each time), which is much lighter for stories
    with hundreds/thousands of chapters. Already thread-safe (uses a lock) so it is safe to
    call from several parallel download workers at once.
    """

    def __init__(self, story_id: str):
        self.story_id = story_id
        self._lock = threading.Lock()
        self._data = load_progress(story_id)

    def has(self, part_id) -> bool:
        return str(part_id) in self._data

    def get(self, part_id):
        return self._data.get(str(part_id))

    def mark_done(self, part_id, title: str, text: str) -> None:
        with self._lock:
            self._data[str(part_id)] = {"title": title, "text": text}
            self._flush()

    def _flush(self) -> None:
        PROGRESS_DIR.mkdir(parents=True, exist_ok=True)
        _progress_path(self.story_id).write_text(
            json.dumps(self._data, ensure_ascii=False), encoding="utf-8"
        )

    def clear(self) -> None:
        with self._lock:
            self._data = {}
            clear_progress(self.story_id)
