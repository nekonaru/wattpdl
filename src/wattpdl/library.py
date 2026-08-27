"""
Modul "perpustakaan" — mencatat cerita yang pernah berhasil diunduh PENUH
(semua chapter, lewat mode 1/2), beserta jumlah chapter saat itu. Dipakai
untuk fitur `--check-updates`: bandingkan jumlah chapter yang tercatat di
sini dengan jumlah chapter saat ini di Wattpad, supaya user tahu cerita
ongoing mana saja yang ada chapter barunya tanpa perlu buka satu-satu.

Sengaja terpisah dari `progress` (yang urusannya resume unduhan yang lagi
berjalan/terhenti) dan `metacache` (cache jangka pendek beberapa menit) —
data di sini dimaksudkan bertahan lama (sampai user unduh ulang cerita itu).
"""
import json
import pathlib

LIBRARY_FILE = pathlib.Path.home() / ".wattpdl" / "library.json"


def load_library() -> dict:
    """Kembalikan semua cerita yang tercatat: {story_id: {"title", "num_parts"}}."""
    if not LIBRARY_FILE.exists():
        return {}
    try:
        return json.loads(LIBRARY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def remember_story(story_id: str, title: str, num_parts: int) -> None:
    """Catat/perbarui 1 cerita di library, dipanggil setelah cerita itu
    berhasil diunduh PENUH (mode 1/2, tanpa chapter gagal)."""
    library = load_library()
    library[str(story_id)] = {"title": title, "num_parts": num_parts}
    try:
        LIBRARY_FILE.parent.mkdir(parents=True, exist_ok=True)
        LIBRARY_FILE.write_text(json.dumps(library, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass
