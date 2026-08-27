"""
Modul cache metadata cerita jangka pendek (TTL beberapa menit).

Dipakai supaya kalau user menjalankan wattpdl beberapa kali berturut-turut
untuk cerita yang sama dalam waktu singkat (mis. lagi coba-coba beberapa
pilihan mode/format sebelum benar-benar unduh, atau script otomatisasi yang
memanggil wattpdl berkali-kali untuk cerita yang sama), tidak perlu fetch API
Wattpad ulang tiap kali — cukup pakai hasil fetch sebelumnya yang masih segar.

TIDAK dipakai untuk keperluan jangka panjang (itu urusan modul `library`) —
TTL sengaja pendek supaya info cerita (jumlah chapter dst.) tetap akurat
kalau memang ada perubahan di Wattpad.
"""
import json
import pathlib
import time

CACHE_DIR = pathlib.Path.home() / ".wattpdl" / "cache"
TTL_SECONDS = 300  # 5 menit


def _cache_path(story_id: str) -> pathlib.Path:
    return CACHE_DIR / f"{story_id}.json"


def get_cached_story(story_id: str):
    """Kembalikan (title, author, parts, meta) dari cache kalau masih segar
    (belum lewat TTL_SECONDS), None kalau belum ada/sudah kedaluwarsa/rusak."""
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
    """Simpan hasil fetch info cerita ke cache. Kegagalan tulis (disk penuh,
    tidak ada izin, dll) tidak boleh mengganggu alur utama — cache cuma
    optimisasi, bukan bagian penting."""
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
