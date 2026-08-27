"""
Modul komunikasi ke Wattpad public API.
Berisi semua fungsi yang mengambil data mentah dari internet
(info cerita & teks chapter), tanpa urusan tampilan atau penulisan file.
"""
import re
import threading
import time
from typing import Optional

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
    "?fields=id,title,description,cover,tags,createDate,completed,"
    "user(name),numParts,parts(id,title)"
)
CHAPTER_TEXT_URL = "https://www.wattpad.com/apiv2/storytext?id={part_id}"

# CATATAN endpoint ini (get_author_stories) mengikuti pola URL API v3 publik
# Wattpad yang sama dengan STORY_INFO_URL di atas, tapi belum sempat
# diverifikasi langsung ke server asli karena lingkungan pengembangan ini
# tidak mempunyai akses jaringan ke wattpad.com. Kalau ternyata struktur
# JSON respons berbeda di lapangan, cukup sesuaikan parsing di
# `get_author_stories()` — bentuk fungsi & pemanggilnya tidak perlu berubah.
AUTHOR_STORIES_URL = (
    "https://www.wattpad.com/api/v3/users/{username}/stories/published"
    "?fields=stories(id,title,numParts,completed)"
)

DELAY_SECONDS = 0.5   # jeda dasar antar chapter (jangan dihapus)
MAX_RETRIES = 3


class WattpadAPIError(Exception):
    """Kelas dasar untuk semua error API Wattpad yang sudah diberi pesan spesifik."""


class StoryNotFoundError(WattpadAPIError):
    """Cerita tidak ditemukan — dihapus penulisnya, atau ID/link salah."""


class StoryAccessError(WattpadAPIError):
    """Cerita ada tapi tidak bisa diakses (private/dibatasi)."""


class AdaptiveRateLimiter:
    """State jeda antar-request yang dibagi bareng semua chapter (dan semua
    worker kalau unduh paralel), supaya proses unduh otomatis melambat kalau
    Wattpad mulai balikin rate-limit (429) atau server sibuk (503) beruntun,
    lalu pelan-pelan kembali cepat begitu request sukses lagi. Thread-safe.
    """

    def __init__(self, base_delay: float = DELAY_SECONDS, max_delay: float = 10.0):
        self._lock = threading.Lock()
        self.base_delay = base_delay
        self.max_delay = max_delay
        self._level = 0  # 0 = kecepatan normal, makin besar makin lambat

    @property
    def current_delay(self) -> float:
        with self._lock:
            return min(self.max_delay, self.base_delay * (2 ** self._level))

    def report_throttled(self) -> None:
        """Panggil tiap kali dapat respons 429/503."""
        with self._lock:
            self._level += 1

    def report_success(self) -> None:
        """Panggil tiap kali request sukses — turunkan level pelan-pelan (bukan
        langsung ke 0, supaya tidak langsung ngebut lagi begitu 1 request
        kebetulan lolos di tengah kondisi server yang masih sibuk)."""
        with self._lock:
            if self._level > 0:
                self._level -= 1

    def wait(self) -> None:
        time.sleep(self.current_delay)


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


def _raise_specific_http_error(e: requests.HTTPError, context: str = "cerita") -> None:
    """Ubah requests.HTTPError generik jadi pesan yang jelas berdasarkan status code."""
    status = e.response.status_code if e.response is not None else None
    if status == 404:
        raise StoryNotFoundError(
            f"{context.capitalize()} tidak ditemukan. Kemungkinan sudah dihapus "
            "penulisnya, akun penulisnya sudah nonaktif, atau ID/link yang "
            "dimasukkan salah."
        ) from e
    if status in (401, 403):
        raise StoryAccessError(
            f"{context.capitalize()} ini private atau dibatasi aksesnya, sehingga "
            "tidak bisa diambil lewat API publik Wattpad."
        ) from e
    raise e


def get_story_info(story_id: str) -> tuple[str, str, list, dict]:
    """
    Ambil metadata cerita: judul, penulis, daftar chapter, dan metadata tambahan.
    Metadata tambahan (dict `meta`) dipakai untuk memperkaya file .docx/.epub:
      - cover_url    : URL gambar sampul cerita (atau None kalau tidak ada)
      - description  : sinopsis/deskripsi cerita
      - tags         : list genre/tag cerita
      - create_date  : tanggal cerita pertama dibuat, apa adanya dari API
      - completed    : True kalau cerita sudah ditandai selesai oleh penulis

    Raise StoryNotFoundError / StoryAccessError dengan pesan yang jelas kalau
    cerita tidak ditemukan / tidak bisa diakses, alih-alih requests.HTTPError
    generik.
    """
    url = STORY_INFO_URL.format(story_id=story_id)
    resp = requests.get(url, headers=HEADERS, timeout=20)
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        _raise_specific_http_error(e, context="cerita")
    data = resp.json()
    title = data.get("title", f"story_{story_id}")
    author = data.get("user", {}).get("name", "unknown")
    parts = data.get("parts", [])
    meta = {
        "cover_url": data.get("cover") or None,
        "description": (data.get("description") or "").strip(),
        "tags": [t for t in (data.get("tags") or []) if t],
        "create_date": data.get("createDate", ""),
        "completed": bool(data.get("completed", False)),
    }
    return title, author, parts, meta


def get_author_stories(username: str) -> list:
    """
    Ambil daftar cerita yang dipublikasikan seorang penulis Wattpad.
    Kembalikan list dict: [{"id": str, "title": str, "num_parts": int, "completed": bool}, ...]

    Dipakai untuk fitur `--user <username>` (unduh semua/cerita pilihan dari
    satu penulis sekaligus, tanpa perlu cari ID satu-satu).
    """
    url = AUTHOR_STORIES_URL.format(username=username)
    resp = requests.get(url, headers=HEADERS, timeout=20)
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        _raise_specific_http_error(e, context="akun penulis")
    data = resp.json()
    stories = data.get("stories", [])
    return [
        {
            "id": str(s.get("id")),
            "title": s.get("title", f"story_{s.get('id')}"),
            "num_parts": s.get("numParts", 0),
            "completed": bool(s.get("completed", False)),
        }
        for s in stories
    ]


def download_cover_image(cover_url: str) -> Optional[bytes]:
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


def download_image(image_url: str) -> Optional[bytes]:
    """Unduh 1 gambar generik (dipakai untuk gambar inline di dalam chapter).
    Sama seperti download_cover_image: kegagalan tidak boleh menggagalkan
    seluruh proses, gambar inline cuma pelengkap — kembalikan None saat gagal.
    """
    if not image_url:
        return None
    try:
        resp = requests.get(image_url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        return resp.content
    except requests.RequestException:
        return None


def get_chapter_html(
    part_id: int,
    retries: int = MAX_RETRIES,
    on_retry=None,
    rate_limiter: Optional[AdaptiveRateLimiter] = None,
) -> str:
    """
    Unduh HTML teks chapter dengan retry otomatis.
    on_retry: callback opsional dipanggil dengan (attempt, retries, wait, error)
    tiap kali percobaan gagal — dipakai CLI untuk menampilkan pesan warning
    tanpa modul ini perlu tahu soal `rich`/console.
    rate_limiter: opsional, kalau diisi maka respons 429/503 akan melaporkan
    diri ke rate limiter supaya jeda antar-chapter otomatis diperlambat.
    """
    if retries < 1:
        raise ValueError("retries harus >= 1")

    url = CHAPTER_TEXT_URL.format(part_id=part_id)
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            if rate_limiter:
                rate_limiter.report_success()
            return resp.text
        except requests.RequestException as e:
            status = getattr(getattr(e, "response", None), "status_code", None)
            if rate_limiter and status in (429, 503):
                rate_limiter.report_throttled()
            if attempt == retries:
                raise
            wait = attempt * 2
            if on_retry:
                on_retry(attempt, retries, wait, e)
            time.sleep(wait)


_IMG_SRC_RE = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)


def extract_chapter_images(html: str) -> list:
    """Cari semua URL gambar inline (tag <img>) di dalam HTML 1 chapter, dalam
    urutan kemunculannya di teks. Dipakai untuk fitur unduh gambar inline
    (bukan cuma cover) ke .docx/.epub/.pdf.
    """
    return _IMG_SRC_RE.findall(html or "")
