"""
Modul komunikasi ke Wattpad public API.
Berisi semua fungsi yang mengambil data mentah dari internet
(info cerita & teks chapter), tanpa urusan tampilan atau penulisan file.
"""
import re
import time

import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

STORY_INFO_URL = (
    "https://www.wattpad.com/api/v3/stories/{story_id}"
    "?fields=id,title,user(name),numParts,parts(id,title)"
)
CHAPTER_TEXT_URL = "https://www.wattpad.com/apiv2/storytext?id={part_id}"

DELAY_SECONDS = 0.5   # jeda antar chapter (jangan dihapus)
MAX_RETRIES = 3


def extract_story_id(user_input: str) -> str:
    """Terima link penuh atau ID angka, kembalikan ID cerita saja."""
    user_input = user_input.strip()
    match = re.search(r"story/(\d+)", user_input)
    if match:
        return match.group(1)
    if user_input.isdigit():
        return user_input
    raise ValueError(
        "Link atau ID cerita tidak dikenali.\n"
        "Contoh link : https://www.wattpad.com/story/398440633-judul-cerita\n"
        "Contoh ID   : 398440633"
    )


def get_story_info(story_id: str) -> tuple[str, str, list]:
    """Ambil metadata cerita: judul, penulis, dan daftar chapter."""
    url = STORY_INFO_URL.format(story_id=story_id)
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    title = data.get("title", f"story_{story_id}")
    author = data.get("user", {}).get("name", "unknown")
    parts = data.get("parts", [])
    return title, author, parts


def get_chapter_html(part_id: int, retries: int = MAX_RETRIES, on_retry=None) -> str:
    """
    Unduh HTML teks chapter dengan retry otomatis.
    on_retry: callback opsional dipanggil dengan (attempt, retries, wait, error)
    tiap kali percobaan gagal — dipakai CLI untuk menampilkan pesan warning
    tanpa modul ini perlu tahu soal `rich`/console.
    """
    url = CHAPTER_TEXT_URL.format(part_id=part_id)
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as e:
            if attempt == retries:
                raise
            wait = attempt * 2
            if on_retry:
                on_retry(attempt, retries, wait, e)
            time.sleep(wait)
    return ""
