"""
Modul resume/progress: menyimpan chapter yang sudah berhasil diunduh untuk
suatu cerita, supaya kalau proses terhenti di tengah jalan (macet, koneksi
putus, terminal ditutup), menjalankan ulang dengan cerita yang sama akan
melanjutkan dari chapter terakhir yang berhasil — bukan mengulang dari awal.

Disimpan per cerita di ~/.wattpdl/progress/<story_id>.json
"""
import json
import pathlib
import threading

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
    """Simpan satu chapter yang baru berhasil diunduh ke file progress cerita ini.

    Dipertahankan sebagai fungsi berdiri sendiri untuk kompatibilitas & pemakaian
    sederhana (baca-ubah-tulis sekali). Untuk sesi unduh banyak chapter
    berturut-turut, pakai `ProgressStore` di bawah — itu baca file cuma sekali
    di awal lalu simpan state di memori, supaya nggak perlu baca ulang seluruh
    JSON tiap 1 chapter selesai (O(n) per save, bukan O(n) baca + O(n) tulis
    berulang untuk tiap chapter = O(n^2) total untuk cerita panjang).
    """
    data = load_progress(story_id)
    data[str(part_id)] = {"title": title, "text": text}
    PROGRESS_DIR.mkdir(parents=True, exist_ok=True)
    _progress_path(story_id).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def clear_progress(story_id: str) -> None:
    """Hapus file progress cerita ini (dipanggil setelah semua chapter berhasil diunduh)."""
    path = _progress_path(story_id)
    if path.exists():
        path.unlink()


class ProgressStore:
    """Pegang progress satu cerita di memori selama satu sesi unduh berlangsung.

    Dipakai oleh `cli.download_chapters()` supaya tiap chapter yang selesai
    diunduh cukup update dict di memori + tulis ulang ke disk sekali (tanpa
    baca ulang file dari awal tiap kali) — jauh lebih ringan untuk cerita
    dengan ratusan/ribuan chapter. Sudah thread-safe (pakai lock) supaya aman
    dipanggil dari beberapa worker unduhan paralel sekaligus.
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
