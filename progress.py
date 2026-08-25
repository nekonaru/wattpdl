"""
Modul resume/progress: menyimpan chapter yang sudah berhasil diunduh untuk
suatu cerita, supaya kalau proses terhenti di tengah jalan (macet, koneksi
putus, terminal ditutup), menjalankan ulang dengan cerita yang sama akan
melanjutkan dari chapter terakhir yang berhasil — bukan mengulang dari awal.

Disimpan per cerita di ~/.wattpdl/progress/<story_id>.json
"""
import json
import pathlib

PROGRESS_DIR = pathlib.Path.home() / ".wattpdl" / "progress"


def _progress_path(story_id: str) -> pathlib.Path:
    return PROGRESS_DIR / f"{story_id}.json"


def load_progress(story_id: str) -> dict:
    """
    Kembalikan chapter yang sudah tersimpan untuk cerita ini:
    {part_id (str): {"title": ..., "text": ...}}
    Kosong kalau belum pernah ada progress atau filenya rusak.
    """
    path = _progress_path(story_id)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_chapter_progress(story_id: str, part_id, title: str, text: str) -> None:
    """Simpan satu chapter yang baru berhasil diunduh ke file progress cerita ini."""
    data = load_progress(story_id)
    data[str(part_id)] = {"title": title, "text": text}
    PROGRESS_DIR.mkdir(parents=True, exist_ok=True)
    _progress_path(story_id).write_text(json.dumps(data), encoding="utf-8")


def clear_progress(story_id: str) -> None:
    """Hapus file progress cerita ini (dipanggil setelah semua chapter berhasil diunduh)."""
    path = _progress_path(story_id)
    if path.exists():
        path.unlink()
