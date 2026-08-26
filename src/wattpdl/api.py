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
    "?fields=id,title,description,cover,tags,createDate,"
    "user(name),numParts,parts(id,title)"
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

    # Link share/mobile per-chapter Wattpad (mis. wattpad.com/1234567-judul-part)
    # tidak mengandung "story/" dan angkanya adalah ID chapter (part), bukan ID cerita —
    # jadi tidak bisa langsung dipakai di sini. Beri pesan yang jelas alih-alih pesan generik.
    chapter_link = re.search(r"wattpad\.com/(\d+)-", user_input)
    if chapter_link:
        raise ValueError(
            "Link ini mengarah ke satu chapter (part), bukan ke halaman cerita.\n"
            "Buka chapter tersebut di Wattpad, lalu pakai link/judul cerita di bagian atas "
            "halaman (mengandung '/story/'), atau salin ID cerita dari sana.\n"
            "Contoh link cerita : https://www.wattpad.com/story/398440633-judul-cerita"
        )

    raise ValueError(
        "Link atau ID cerita tidak dikenali.\n"
        "Contoh link : https://www.wattpad.com/story/398440633-judul-cerita\n"
        "Contoh ID   : 398440633"
    )


def get_story_info(story_id: str) -> tuple[str, str, list, dict]:
    """
    Ambil metadata cerita: judul, penulis, daftar chapter, dan metadata tambahan.
    Metadata tambahan (dict `meta`) dipakai untuk memperkaya file .docx/.epub:
      - cover_url    : URL gambar sampul cerita (atau None kalau tidak ada)
      - description  : sinopsis/deskripsi cerita
      - tags         : list genre/tag cerita
      - create_date  : tanggal cerita pertama dibuat, apa adanya dari API
    """
    url = STORY_INFO_URL.format(story_id=story_id)
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    title = data.get("title", f"story_{story_id}")
    author = data.get("user", {}).get("name", "unknown")
    parts = data.get("parts", [])
    meta = {
        "cover_url": data.get("cover") or None,
        "description": (data.get("description") or "").strip(),
        "tags": [t for t in (data.get("tags") or []) if t],
        "create_date": data.get("createDate", ""),
    }
    return title, author, parts, meta


def download_cover_image(cover_url: str) -> bytes | None:
    """
    Unduh gambar sampul cerita. Dipakai untuk menyisipkan cover di file .docx/.epub.
    Kegagalan di sini tidak boleh menghentikan proses unduh cerita — cover cuma
    pemanis, bukan bagian penting — jadi selalu kembalikan None saat gagal,
    tidak raise exception.
    """
    if not cover_url:
        return None
    try:
        resp = requests.get(cover_url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        return resp.content
    except requests.RequestException:
        return None


def get_chapter_html(part_id: int, retries: int = MAX_RETRIES, on_retry=None) -> str:
    """
    Unduh HTML teks chapter dengan retry otomatis.
    on_retry: callback opsional dipanggil dengan (attempt, retries, wait, error)
    tiap kali percobaan gagal — dipakai CLI untuk menampilkan pesan warning
    tanpa modul ini perlu tahu soal `rich`/console.
    """
    if retries < 1:
        raise ValueError("retries harus >= 1")

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
