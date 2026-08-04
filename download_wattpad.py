import os
import re
import sys
import time
import pathlib
import requests

# ─────────────────────────────────────────────
#  Konfigurasi
# ─────────────────────────────────────────────

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
MAX_RETRIES   = 3     # maksimal percobaan ulang per chapter


# ─────────────────────────────────────────────
#  Fungsi Utilitas
# ─────────────────────────────────────────────

def get_default_download_dir() -> pathlib.Path:
    """
    Kembalikan folder Downloads bawaan sistem operasi:
      - Windows : C:\\Users\\<user>\\Downloads
      - macOS   : /Users/<user>/Downloads
      - Linux   : /home/<user>/Downloads  (atau XDG_DOWNLOAD_DIR)
    """
    # Cek XDG_DOWNLOAD_DIR (Linux/freedesktop standard)
    xdg = os.environ.get("XDG_DOWNLOAD_DIR", "").strip()
    if xdg and pathlib.Path(xdg).is_dir():
        return pathlib.Path(xdg)

    # Fallback universal: ~/Downloads
    downloads = pathlib.Path.home() / "Downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    return downloads


def extract_story_id(user_input: str) -> str:
    """Terima link penuh atau ID angka, kembalikan ID cerita saja."""
    user_input = user_input.strip()
    # Contoh: https://www.wattpad.com/story/398440633-langit-bandung
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
    url  = STORY_INFO_URL.format(story_id=story_id)
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    data   = resp.json()
    title  = data.get("title", f"story_{story_id}")
    author = data.get("user", {}).get("name", "unknown")
    parts  = data.get("parts", [])
    return title, author, parts


def get_chapter_html(part_id: int, retries: int = MAX_RETRIES) -> str:
    """Unduh HTML teks chapter dengan retry otomatis."""
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
            print(f"    ⚠  Gagal (percobaan {attempt}/{retries}), coba lagi dalam {wait}s… ({e})")
            time.sleep(wait)
    return ""   # tidak akan tercapai, tapi memuaskan type-checker


def html_to_text(html: str) -> str:
    """Konversi HTML Wattpad ke teks bersih."""
    text = re.sub(r"</p>",       "\n\n", html, flags=re.IGNORECASE)
    text = re.sub(r"<br\s*/?>",  "\n",   text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>",   "",     text)
    text = re.sub(r"\n{3,}",    "\n\n", text)
    return text.strip()


def safe_filename(name: str) -> str:
    """Buat nama file yang aman untuk semua sistem operasi."""
    # Hapus karakter ilegal Windows/Linux/macOS
    name = re.sub(r'[<>:"/\\|?*]', "", name)
    name = re.sub(r"[^\w\s\-]", "", name).strip()
    name = re.sub(r"\s+", "_", name)
    return name or "cerita_wattpad"


def progress_bar(current: int, total: int, width: int = 30) -> str:
    """Tampilkan progress bar sederhana di terminal."""
    filled = int(width * current / total)
    bar    = "█" * filled + "░" * (width - filled)
    pct    = current / total * 100
    return f"[{bar}] {pct:5.1f}%  ({current}/{total})"


# ─────────────────────────────────────────────
#  Program Utama
# ─────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  Wattpad Downloader — simpan cerita ke file .txt  ")
    print("=" * 55)

    # ── 1. Input link / ID ──────────────────────────────────
    raw = input("\nMasukkan link atau ID cerita Wattpad: ").strip()
    try:
        story_id = extract_story_id(raw)
    except ValueError as e:
        print(f"\n❌  {e}")
        sys.exit(1)

    # ── 2. Ambil info cerita ────────────────────────────────
    print(f"\n⏳  Mengambil info cerita (ID: {story_id})…")
    try:
        title, author, parts = get_story_info(story_id)
    except requests.HTTPError as e:
        print(f"❌  Gagal mengakses API Wattpad: {e}")
        print("    Pastikan ID/link benar dan cerita tidak di-private.")
        sys.exit(1)

    if not parts:
        print("❌  Tidak ada chapter ditemukan. Cek lagi ID/link ceritanya.")
        sys.exit(1)

    print(f'\n📖  "{title}" oleh {author}')
    print(f"    {len(parts)} chapter ditemukan.\n")

    # ── 3. Pilih folder simpan ──────────────────────────────
    default_dir = get_default_download_dir()
    print(f"📁  Folder default penyimpanan: {default_dir}")
    custom = input(
        "    Tekan Enter untuk memakai folder itu,\n"
        "    atau ketik path lain (misal: D:\\Cerita atau /home/niko/cerita):\n"
        "    > "
    ).strip()

    if custom:
        save_dir = pathlib.Path(custom).expanduser().resolve()
        try:
            save_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(f"❌  Folder tidak bisa dibuat: {e}")
            print(f"    Menggunakan folder default: {default_dir}")
            save_dir = default_dir
    else:
        save_dir = default_dir

    filename  = f"{safe_filename(title)}.txt"
    full_path = save_dir / filename

    print(f"\n💾  File akan disimpan di:\n    {full_path}\n")

    # ── 4. Unduh chapter satu per satu ─────────────────────
    failed_chapters: list[str] = []

    with open(full_path, "w", encoding="utf-8") as f:
        # Header file
        f.write(f"{title}\n")
        f.write(f"oleh {author}\n")
        f.write(f"Sumber : https://www.wattpad.com/story/{story_id}\n")
        f.write(f"\n{'=' * 50}\n\n")

        for i, part in enumerate(parts, start=1):
            part_id       = part["id"]
            chapter_title = part.get("title", f"Chapter {i}")

            # Progress bar
            print(f"\r{progress_bar(i - 1, len(parts))}  {chapter_title[:30]:<30}", end="", flush=True)

            try:
                html = get_chapter_html(part_id)
                text = html_to_text(html)
            except Exception as e:
                print(f"\n    ⚠  Chapter [{i}] gagal: {e}")
                text = "[GAGAL DIUNDUH — coba jalankan ulang]"
                failed_chapters.append(f"Chapter {i}: {chapter_title}")

            f.write(f"\n\n{'#' * 5} {chapter_title} {'#' * 5}\n\n")
            f.write(text)
            f.write("\n")

            time.sleep(DELAY_SECONDS)

    # Progress bar 100%
    print(f"\r{progress_bar(len(parts), len(parts))}  Selesai!               ", flush=True)

    # ── 5. Ringkasan ────────────────────────────────────────
    print(f"\n✅  Semua chapter tersimpan di:")
    print(f"    {full_path}")

    if failed_chapters:
        print(f"\n⚠️   {len(failed_chapters)} chapter gagal diunduh:")
        for ch in failed_chapters:
            print(f"    - {ch}")
        print("    Jalankan ulang script untuk mencoba lagi.")
    else:
        print(f"\n🎉  Berhasil! {len(parts)} chapter terunduh tanpa error.")

    print()


if __name__ == "__main__":
    main()
