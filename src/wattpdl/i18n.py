"""
Translation module (i18n) for the CLI display: English (default) and Bahasa Indonesia.

Pure data + small functions. It must not know about `rich`, the network, or the CLI,
so it can be used from any module (api, writers, cli, app).

Order for determining the display language (the topmost wins):
  1. argument  --ui-lang id|en
  2. env var   WATTPDL_LANG=id|en
  3. config    "ui_lang" in ~/.wattpdl/config.json
  4. default   "en"

Note: this is DIFFERENT from `--lang`, which only sets the language metadata in EPUB files.
"""
import os

SUPPORTED = ("id", "en")
DEFAULT_LANG = "en"

_current = {"lang": DEFAULT_LANG}


def normalize(code) -> str:
    """Turn any input ('EN', 'en_US', 'id-ID', None) into 'id'/'en'. Unrecognized -> None."""
    if not code:
        return None
    base = str(code).strip().lower().replace("_", "-").split("-")[0]
    return base if base in SUPPORTED else None


def resolve_language(cli_value=None, config_value=None, env=None) -> str:
    """Determine the display language from argument > env > config > default (en)."""
    env = os.environ if env is None else env
    for candidate in (cli_value, env.get("WATTPDL_LANG"), config_value):
        lang = normalize(candidate)
        if lang:
            return lang
    return DEFAULT_LANG


def set_language(code) -> str:
    lang = normalize(code) or DEFAULT_LANG
    _current["lang"] = lang
    return lang


def get_language() -> str:
    return _current["lang"]


def t(key: str, **kwargs) -> str:
    """Get the text for `key` in the active language. Fallback: the default language (English), then the key itself."""
    table = MESSAGES.get(_current["lang"], {})
    text = table.get(key)
    if text is None:
        text = MESSAGES[DEFAULT_LANG].get(key, key)
    return text.format(**kwargs) if kwargs else text


MESSAGES = {
    "id": {
        # ---------- cli.py ----------
        "step.pick_chapter": "Pilih Chapter",
        "unit.seconds": "d",
        "warn.file_exists": "⚠  File sudah ada:",
        "prompt.overwrite": "Timpa file ini?",
        "table.no": "No",
        "table.chapter_title": "Judul Chapter",
        "table.title": "Judul",
        "table.chapters": "Chapter",
        "err.empty_input": "Input tidak boleh kosong.",
        "err.bad_range": "Format rentang tidak valid: '{chunk}'",
        "err.not_number": "'{chunk}' bukan angka yang valid.",
        "err.no_valid_chapter": "Tidak ada nomor chapter valid (rentang 1-{total}).",
        "prompt.chapter_numbers": "Masukkan nomor chapter",
        "prompt.chapter_numbers_hint": "(contoh: 1,3,5-8)",
        "ok.chapters_selected": "✔ {n} chapter dipilih.",
        "err.number_between": "❌  Masukkan angka antara 1-{total}.",
        "ok.selected": "✔ Dipilih:",
        "retry.failed": "    ⚠  Gagal (percobaan {attempt}/{retries}), coba lagi dalam {wait}s… ({error})",
        "chapter.failed_placeholder": "[GAGAL DIUNDUH: coba jalankan ulang]",
        "progress.preparing": "Menyiapkan…",
        "progress.remaining": "sisa",
        "progress.chapter_count": "{done}/{total} chapter",
        "err.chapter_failed": "\n    ⚠  Chapter [{idx}] gagal:",
        "info.resumed": "↻ {n} chapter dipakai dari progress sebelumnya (tidak diunduh ulang).",

        # ---------- app.py : umum ----------
        "err.folder_create": "\n❌  Folder tidak bisa dibuat:",
        "err.folder_default_create": "❌  Folder default juga tidak bisa dibuat:",
        "hint.other_folder": "    Coba jalankan ulang dengan folder simpan lain yang kamu punya izin tulis di sana.",
        "info.using_default_folder": "    Menggunakan folder default: {path}",
        "err.chapter_out_of_range": "❌  Chapter {n} di luar rentang (1-{total}).",
        "err.path_invalid": "\n❌  Nama file/path tidak valid atau terlalu panjang:",
        "info.path_tried": "    Path yang dicoba: {path}",
        "hint.shorter_path": "    Coba pilih folder simpan dengan path yang lebih pendek.",
        "info.skipped_existing_kept": "Dilewati: file yang sudah ada tidak diubah.\n",
        "info.skipped_existing": "⏭  Dilewati: file sudah ada:",
        "hint.remove_skip_existing": "    (hapus --skip-existing kalau mau menimpanya)",
        "info.saved_at": "\n💾 File akan disimpan di:",
        "step.downloading": "Mengunduh Chapter",
        "err.write_failed": "\n❌  Gagal menulis file output:",
        "hint.progress_kept": (
            "    Chapter yang sudah berhasil diunduh tetap tersimpan di progress, "
            "jalankan ulang setelah masalah di atas diperbaiki."
        ),
        "step.summary": "Ringkasan",
        "sum.file_saved": "📁 File tersimpan di",
        "sum.success": "✅ Berhasil",
        "sum.failed": "⚠️  Gagal",
        "sum.total_time": "⏱️  Waktu total",
        "sum.failed_chapters": "Chapter yang gagal:",
        "sum.title_partial": "⚠️  Selesai dengan beberapa kegagalan",
        "sum.partial_hint": (
            "Progress chapter yang sudah berhasil sudah tersimpan, "
            "jalankan ulang cerita yang sama untuk melanjutkan tanpa mengulang dari awal."
        ),
        "sum.title_done": "🎉 Berhasil!  Semua chapter tersimpan",
        "status.fetching_story": "Mengambil info cerita (ID: {story_id})…",
        "err.api_access": "❌  Gagal mengakses API Wattpad:",
        "hint.check_connection": "    Pastikan koneksi internet stabil, dan coba lagi beberapa saat.",
        "err.no_chapters": "❌  Tidak ada chapter ditemukan. Cek lagi ID/link ceritanya.",

        # ---------- app.py : story info ----------
        "step.story_info": "Info Cerita",
        "info.title": "📌 Judul",
        "info.author": "✍️  Penulis",
        "info.chapter_count": "📚 Jumlah chapter",

        # ---------- app.py : interaktif ----------
        "tagline": "📖 Wattpad Story Downloader",
        "tagline_sub": "-  simpan cerita jadi file .txt/.docx/.epub/.md/.pdf offline",
        "step.enter_story": "Masukkan Cerita",
        "prompt.story": "Link atau ID cerita Wattpad",
        "step.pick_mode": "Pilih Mode Unduh",
        "mode.1": "Semua chapter → 1 file gabungan",
        "mode.2": "Semua chapter → file terpisah per chapter, dikemas .zip",
        "mode.3": "Pilih beberapa chapter → 1 file gabungan",
        "mode.4": "Pilih 1 chapter saja",
        "prompt.mode": "Pilih mode",
        "fmt.1": "Teks polos (.txt)",
        "fmt.2": "Dokumen Word (.docx)",
        "fmt.3": "Ebook (.epub)",
        "fmt.4": "Markdown (.md)",
        "fmt.5": "PDF (.pdf)",
        "prompt.format": "Pilih format file",
        "prompt.include_images": "Ikut unduh & sisipkan gambar di dalam teks chapter (bukan cuma cover)?",
        "prompt.parallel": "Percepat unduhan dengan mengunduh beberapa chapter sekaligus (paralel)?",
        "prompt.workers": "Berapa chapter sekaligus? (disarankan 3-5)",
        "step.save_folder": "Folder Penyimpanan",
        "info.default_folder": "Folder default:",
        "prompt.custom_folder": "Tekan Enter untuk pakai folder itu, atau ketik path lain",

        # ---------- app.py : --user ----------
        "err.user_mode_only_12": (
            "❌  --user hanya mendukung --mode 1 atau 2 "
            "(unduh chapter tertentu tidak berlaku untuk banyak cerita sekaligus)."
        ),
        "step.story_list": "Daftar Cerita: {user}",
        "status.fetching_user_stories": "Mengambil daftar cerita milik '{user}'…",
        "err.no_user_stories": "❌  Tidak ada cerita ditemukan untuk penulis '{user}'.",
        "err.user_select_invalid": "❌  --user-select tidak valid: {error}",
        "ok.stories_selected": "\n✔ {n} dari {total} cerita akan diunduh.",
        "info.story_progress": "\n- Cerita {n}/{total}: {title}",

        # ---------- app.py : --check-updates ----------
        "step.check_updates": "Cek Update Cerita",
        "info.library_empty": (
            "Belum ada cerita yang tercatat. Cerita otomatis tercatat setelah "
            "berhasil diunduh penuh lewat mode 1 atau 2."
        ),
        "table.recorded_chapters": "Chapter Tercatat",
        "table.current_chapters": "Chapter Sekarang",
        "table.status": "Status",
        "status.deleted": "❌ dihapus/tidak ditemukan",
        "status.check_failed": "⚠ gagal cek",
        "status.new_chapters": "✨ +{n} chapter baru",
        "status.up_to_date": "sudah terbaru",
        "info.updates_available": (
            "\nAda cerita dengan chapter baru, jalankan ulang unduhan normal "
            "(mode 1/2) untuk cerita itu untuk memperbarui filenya."
        ),

        # ---------- app.py : --watch ----------
        "watch.active": (
            "\n👀 Mode watch aktif untuk cerita ID {story_id}. "
            "Cek tiap {interval} detik. Tekan Ctrl+C untuk berhenti.\n"
        ),
        "watch.check_failed": "⚠  Gagal cek update (percobaan #{iteration}): {error}",
        "watch.new_chapters": "\n✨ Chapter baru terdeteksi! ({old} → {new} chapter). Mengunduh ulang…",
        "watch.no_new": "↻ Belum ada chapter baru ({n} chapter). Cek lagi dalam {interval} detik…",
        "watch.max_reached": "Batas jumlah pengecekan tercapai, mode watch berhenti.",
        "watch.stopped": "\nMode watch dihentikan.",

        # ---------- app.py : update check ----------
        "update.available": "💡 Versi baru wattpdl tersedia: {latest}. Update dengan:",

        # ---------- writers.py ----------
        "lib.missing": "\n❌  Library '{lib}' belum terinstall.",
        "lib.run": "    Jalankan:",
        "lib.missing_plain": "Library '{lib}' belum terinstall. Jalankan: pip install {lib}",

        # ---------- api.py ----------
        "api.chapter_link": (
            "Link ini mengarah ke satu chapter (part), bukan ke halaman cerita.\n"
            "Buka chapter tersebut di Wattpad, lalu pakai link/judul cerita di bagian atas "
            "halaman (mengandung '/story/'), atau salin ID cerita dari sana.\n"
            "Contoh link cerita : https://www.wattpad.com/story/398440633-judul-cerita"
        ),
        "api.unrecognized": (
            "Link atau ID cerita tidak dikenali.\n"
            "Contoh link : https://www.wattpad.com/story/398440633-judul-cerita\n"
            "Contoh ID   : 398440633"
        ),
        "api.context_story": "cerita",
        "api.context_author": "akun penulis",
        "api.not_found": (
            "{context} tidak ditemukan. Kemungkinan sudah dihapus "
            "penulisnya, akun penulisnya sudah nonaktif, atau ID/link yang "
            "dimasukkan salah."
        ),
        "api.private": (
            "{context} ini private atau dibatasi aksesnya, sehingga "
            "tidak bisa diambil lewat API publik Wattpad."
        ),

        # ---------- cli_args.py : validasi ----------
        "val.mode_required": "--mode wajib diisi kalau pakai --id (mode non-interaktif).",
        "val.chapters_required": "--chapters wajib diisi untuk --mode 3, contoh: --chapters 1,3,5-8",
        "val.chapter_required": "--chapter wajib diisi untuk --mode 4, contoh: --chapter 5",
        "val.workers_min": "--workers minimal 1.",

        # ---------- cli_args.py : help argparse ----------
        "meta.id": "ID_ATAU_LINK",
        "meta.code": "KODE",
        "meta.seconds": "DETIK",
        "help.description": (
            "WattPDL: Wattpad Story Downloader. "
            "Jalankan tanpa argumen untuk mode interaktif, "
            "atau isi --id (atau --user) untuk mode non-interaktif/scripting."
        ),
        "help.mode": (
            "1 = semua chapter jadi 1 file gabungan, "
            "2 = semua chapter terpisah dikemas .zip, "
            "3 = pilih beberapa chapter (perlu --chapters), "
            "4 = pilih 1 chapter saja (perlu --chapter)"
        ),
        "help.id": "ID atau link cerita Wattpad. Mengisi ini mengaktifkan mode non-interaktif.",
        "help.format": "Format file output. Default: dari config tersimpan, atau txt kalau belum ada.",
        "help.chapters": "Nomor chapter yang diunduh untuk --mode 3, contoh: 1,3,5-8",
        "help.chapter": "Nomor chapter yang diunduh untuk --mode 4",
        "help.output_dir": "Folder penyimpanan. Default: dari config tersimpan, atau folder Downloads.",
        "help.skip_existing": "Lewati unduhan kalau file output tujuan sudah ada, alih-alih menimpanya.",
        "help.no_cover": "Jangan sisipkan gambar sampul cerita ke file .docx/.epub/.pdf.",
        "help.include_images": (
            "Ikut unduh & sisipkan gambar inline di dalam chapter (bukan cuma cover) "
            "ke file .docx/.epub/.pdf. Menambah waktu unduh."
        ),
        "help.workers": (
            "Jumlah chapter yang diunduh bersamaan (paralel). Default 1 (berurutan, "
            "paling aman). Naikkan (mis. 4) untuk mempercepat cerita panjang; jeda "
            "otomatis melambat sendiri kalau server mulai membatasi (rate-limit)."
        ),
        "help.no_cache": "Jangan pakai cache metadata cerita (~/.wattpdl/cache/), selalu ambil data terbaru.",
        "help.lang": (
            "Kode bahasa ISO 639-1 utk metadata EPUB (default: id). Isi 'en' kalau "
            "ceritanya berbahasa Inggris, dst. Tidak memengaruhi format lain."
        ),
        "help.ui_lang": (
            "Bahasa tampilan CLI: id (Indonesia) atau en (English, default). Pilihan ini diingat "
            "untuk sesi berikutnya. Bisa juga lewat env var WATTPDL_LANG."
        ),
        "help.no_update_check": "Jangan cek versi wattpdl terbaru di PyPI saat start.",
        "help.user": (
            "Unduh dari daftar cerita seorang penulis Wattpad, alih-alih 1 cerita by ID. "
            "Kombinasikan dengan --user-select."
        ),
        "help.user_select": (
            "Cerita mana saja dari --user yang diunduh: 'all' (default) atau nomor "
            "seperti pada --chapters, mis. 1,3,5-8."
        ),
        "help.check_updates": (
            "Cek semua cerita yang pernah diunduh (~/.wattpdl/library.json) apakah ada "
            "chapter baru, tanpa perlu --id. Tidak mengunduh apa pun, cuma melaporkan."
        ),
        "help.watch": (
            "Pantau --id terus-menerus, otomatis unduh ulang kalau ada chapter baru. "
            "Berhenti dengan Ctrl+C."
        ),
        "help.watch_interval": "Jeda antar pengecekan di mode --watch, dalam detik (default 1800 = 30 menit).",
    },

    "en": {
        # ---------- cli.py ----------
        "step.pick_chapter": "Select Chapter",
        "unit.seconds": "s",
        "warn.file_exists": "⚠  File already exists:",
        "prompt.overwrite": "Overwrite this file?",
        "table.no": "No",
        "table.chapter_title": "Chapter Title",
        "table.title": "Title",
        "table.chapters": "Chapters",
        "err.empty_input": "Input cannot be empty.",
        "err.bad_range": "Invalid range format: '{chunk}'",
        "err.not_number": "'{chunk}' is not a valid number.",
        "err.no_valid_chapter": "No valid chapter numbers (range 1-{total}).",
        "prompt.chapter_numbers": "Enter chapter numbers",
        "prompt.chapter_numbers_hint": "(example: 1,3,5-8)",
        "ok.chapters_selected": "✔ {n} chapter(s) selected.",
        "err.number_between": "❌  Enter a number between 1-{total}.",
        "ok.selected": "✔ Selected:",
        "retry.failed": "    ⚠  Failed (attempt {attempt}/{retries}), retrying in {wait}s… ({error})",
        "chapter.failed_placeholder": "[DOWNLOAD FAILED: try running again]",
        "progress.preparing": "Preparing…",
        "progress.remaining": "left",
        "progress.chapter_count": "{done}/{total} chapters",
        "err.chapter_failed": "\n    ⚠  Chapter [{idx}] failed:",
        "info.resumed": "↻ {n} chapter(s) reused from previous progress (not downloaded again).",

        # ---------- app.py : general ----------
        "err.folder_create": "\n❌  Could not create folder:",
        "err.folder_default_create": "❌  Could not create the default folder either:",
        "hint.other_folder": "    Try running again with another save folder that you have write permission for.",
        "info.using_default_folder": "    Using default folder: {path}",
        "err.chapter_out_of_range": "❌  Chapter {n} is out of range (1-{total}).",
        "err.path_invalid": "\n❌  File name/path is invalid or too long:",
        "info.path_tried": "    Path attempted: {path}",
        "hint.shorter_path": "    Try choosing a save folder with a shorter path.",
        "info.skipped_existing_kept": "Skipped: the existing file was left unchanged.\n",
        "info.skipped_existing": "⏭  Skipped: file already exists:",
        "hint.remove_skip_existing": "    (remove --skip-existing if you want to overwrite it)",
        "info.saved_at": "\n💾 File will be saved to:",
        "step.downloading": "Downloading Chapters",
        "err.write_failed": "\n❌  Failed to write output file:",
        "hint.progress_kept": (
            "    Chapters that were already downloaded are kept in progress, "
            "run again after fixing the problem above."
        ),
        "step.summary": "Summary",
        "sum.file_saved": "📁 File saved to",
        "sum.success": "✅ Succeeded",
        "sum.failed": "⚠️  Failed",
        "sum.total_time": "⏱️  Total time",
        "sum.failed_chapters": "Failed chapters:",
        "sum.title_partial": "⚠️  Finished with some failures",
        "sum.partial_hint": (
            "Progress for chapters that succeeded is saved, "
            "run the same story again to continue without starting over."
        ),
        "sum.title_done": "🎉 Success!  All chapters saved",
        "status.fetching_story": "Fetching story info (ID: {story_id})…",
        "err.api_access": "❌  Failed to reach the Wattpad API:",
        "hint.check_connection": "    Make sure your internet connection is stable, then try again in a moment.",
        "err.no_chapters": "❌  No chapters found. Double-check the story ID/link.",

        # ---------- app.py : story info ----------
        "step.story_info": "Story Info",
        "info.title": "📌 Title",
        "info.author": "✍️  Author",
        "info.chapter_count": "📚 Chapter count",

        # ---------- app.py : interactive ----------
        "tagline": "📖 Wattpad Story Downloader",
        "tagline_sub": "-  save stories as offline .txt/.docx/.epub/.md/.pdf files",
        "step.enter_story": "Enter Story",
        "prompt.story": "Wattpad story link or ID",
        "step.pick_mode": "Select Download Mode",
        "mode.1": "All chapters → 1 combined file",
        "mode.2": "All chapters → separate file per chapter, packed as .zip",
        "mode.3": "Select several chapters → 1 combined file",
        "mode.4": "Select 1 chapter only",
        "prompt.mode": "Select mode",
        "fmt.1": "Plain text (.txt)",
        "fmt.2": "Word document (.docx)",
        "fmt.3": "Ebook (.epub)",
        "fmt.4": "Markdown (.md)",
        "fmt.5": "PDF (.pdf)",
        "prompt.format": "Select file format",
        "prompt.include_images": "Also download & embed images inside chapter text (not just the cover)?",
        "prompt.parallel": "Speed up by downloading several chapters at once (parallel)?",
        "prompt.workers": "How many chapters at once? (3-5 recommended)",
        "step.save_folder": "Save Folder",
        "info.default_folder": "Default folder:",
        "prompt.custom_folder": "Press Enter to use that folder, or type another path",

        # ---------- app.py : --user ----------
        "err.user_mode_only_12": (
            "❌  --user only supports --mode 1 or 2 "
            "(downloading specific chapters does not apply to many stories at once)."
        ),
        "step.story_list": "Story List: {user}",
        "status.fetching_user_stories": "Fetching story list for '{user}'…",
        "err.no_user_stories": "❌  No stories found for author '{user}'.",
        "err.user_select_invalid": "❌  Invalid --user-select: {error}",
        "ok.stories_selected": "\n✔ {n} of {total} stories will be downloaded.",
        "info.story_progress": "\n- Story {n}/{total}: {title}",

        # ---------- app.py : --check-updates ----------
        "step.check_updates": "Check Story Updates",
        "info.library_empty": (
            "No stories recorded yet. Stories are recorded automatically after "
            "being fully downloaded with mode 1 or 2."
        ),
        "table.recorded_chapters": "Recorded Chapters",
        "table.current_chapters": "Current Chapters",
        "table.status": "Status",
        "status.deleted": "❌ deleted/not found",
        "status.check_failed": "⚠ check failed",
        "status.new_chapters": "✨ +{n} new chapter(s)",
        "status.up_to_date": "up to date",
        "info.updates_available": (
            "\nSome stories have new chapters, run the normal download again "
            "(mode 1/2) for those stories to refresh their files."
        ),

        # ---------- app.py : --watch ----------
        "watch.active": (
            "\n👀 Watch mode active for story ID {story_id}. "
            "Checking every {interval} seconds. Press Ctrl+C to stop.\n"
        ),
        "watch.check_failed": "⚠  Update check failed (attempt #{iteration}): {error}",
        "watch.new_chapters": "\n✨ New chapters detected! ({old} → {new} chapters). Downloading again…",
        "watch.no_new": "↻ No new chapters yet ({n} chapters). Checking again in {interval} seconds…",
        "watch.max_reached": "Check limit reached, watch mode stopped.",
        "watch.stopped": "\nWatch mode stopped.",

        # ---------- app.py : update check ----------
        "update.available": "💡 A new wattpdl version is available: {latest}. Update with:",

        # ---------- writers.py ----------
        "lib.missing": "\n❌  Library '{lib}' is not installed.",
        "lib.run": "    Run:",
        "lib.missing_plain": "Library '{lib}' is not installed. Run: pip install {lib}",

        # ---------- api.py ----------
        "api.chapter_link": (
            "This link points to a single chapter (part), not to the story page.\n"
            "Open that chapter on Wattpad, then use the story link/title at the top of the "
            "page (it contains '/story/'), or copy the story ID from there.\n"
            "Story link example : https://www.wattpad.com/story/398440633-story-title"
        ),
        "api.unrecognized": (
            "Story link or ID not recognized.\n"
            "Link example : https://www.wattpad.com/story/398440633-story-title\n"
            "ID example   : 398440633"
        ),
        "api.context_story": "story",
        "api.context_author": "author account",
        "api.not_found": (
            "{context} not found. It may have been deleted by the author, "
            "the author's account may be deactivated, or the ID/link "
            "entered is wrong."
        ),
        "api.private": (
            "{context} is private or access-restricted, so it "
            "cannot be fetched through Wattpad's public API."
        ),

        # ---------- cli_args.py : validation ----------
        "val.mode_required": "--mode is required when using --id (non-interactive mode).",
        "val.chapters_required": "--chapters is required for --mode 3, example: --chapters 1,3,5-8",
        "val.chapter_required": "--chapter is required for --mode 4, example: --chapter 5",
        "val.workers_min": "--workers must be at least 1.",

        # ---------- cli_args.py : argparse help ----------
        "meta.id": "ID_OR_LINK",
        "meta.code": "CODE",
        "meta.seconds": "SECONDS",
        "help.description": (
            "WattPDL: Wattpad Story Downloader. "
            "Run with no arguments for interactive mode, "
            "or pass --id (or --user) for non-interactive/scripting mode."
        ),
        "help.mode": (
            "1 = all chapters in 1 combined file, "
            "2 = all chapters as separate files packed in a .zip, "
            "3 = select several chapters (needs --chapters), "
            "4 = select 1 chapter only (needs --chapter)"
        ),
        "help.id": "Wattpad story ID or link. Setting this enables non-interactive mode.",
        "help.format": "Output file format. Default: from saved config, or txt if none yet.",
        "help.chapters": "Chapter numbers to download for --mode 3, example: 1,3,5-8",
        "help.chapter": "Chapter number to download for --mode 4",
        "help.output_dir": "Save folder. Default: from saved config, or the Downloads folder.",
        "help.skip_existing": "Skip the download if the target output file already exists, instead of overwriting it.",
        "help.no_cover": "Do not embed the story cover image in .docx/.epub/.pdf files.",
        "help.include_images": (
            "Also download & embed inline images inside chapters (not just the cover) "
            "in .docx/.epub/.pdf files. Increases download time."
        ),
        "help.workers": (
            "Number of chapters downloaded at the same time (parallel). Default 1 (sequential, "
            "safest). Raise it (e.g. 4) to speed up long stories; the delay "
            "slows down automatically if the server starts rate-limiting."
        ),
        "help.no_cache": "Do not use the story metadata cache (~/.wattpdl/cache/), always fetch fresh data.",
        "help.lang": (
            "ISO 639-1 language code for EPUB metadata (default: id). Use 'en' if the "
            "story is in English, etc. Does not affect other formats."
        ),
        "help.ui_lang": (
            "CLI display language: id (Indonesian) or en (English, default). This choice is remembered "
            "for the next sessions. Can also be set via the WATTPDL_LANG env var."
        ),
        "help.no_update_check": "Do not check for the latest wattpdl version on PyPI at startup.",
        "help.user": (
            "Download from a Wattpad author's story list, instead of 1 story by ID. "
            "Combine with --user-select."
        ),
        "help.user_select": (
            "Which stories from --user to download: 'all' (default) or numbers "
            "like --chapters, e.g. 1,3,5-8."
        ),
        "help.check_updates": (
            "Check every story you have downloaded (~/.wattpdl/library.json) for new "
            "chapters, without needing --id. Downloads nothing, only reports."
        ),
        "help.watch": (
            "Watch --id continuously, automatically re-download when there are new chapters. "
            "Stop with Ctrl+C."
        ),
        "help.watch_interval": "Delay between checks in --watch mode, in seconds (default 1800 = 30 minutes).",
    },
}
