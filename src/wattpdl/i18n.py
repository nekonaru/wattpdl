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
        "warn.parts_mismatch": (
            "⚠  Wattpad mencatat {reported} chapter, tapi hanya {accessible} yang tersedia. "
            "Sebagian chapter mungkin disembunyikan, berbayar, atau belum dipublikasikan, "
            "sehingga tidak bisa diunduh."
        ),
        "status.downloading_cover": "Mengunduh cover…",
        "info.images_downloaded": "🖼  {n} gambar inline berhasil diunduh.",
        "warn.no_images": (
            "⚠  Tidak ada gambar inline yang berhasil diunduh dari chapter ini. "
            "Kalau ceritanya berbasis gambar, mungkin gambarnya tidak tersedia atau diblokir Wattpad."
        ),
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
        "api.context_chapter": "chapter",
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
        "val.retries_min": "--retries minimal 1.",
        "val.retries_max": "--retries maksimal 10.",
        "val.timeout_min": "--timeout minimal 1 detik.",
        "val.json_requires": "--json hanya berlaku untuk --library dan --check-updates.",
        "val.standalone_conflict": "Satu perintah utama per kali (--library, --library-forget, --update-library, --check-updates, --search, --file, --config, --config-set, --doctor, --completion); tidak bisa digabung dengan --id/--user.",
        "val.select_requires_search": "--select butuh --search.",
        "val.search_empty": "--search tidak boleh kosong.",
        "val.search_mode": "--search hanya untuk --mode 1 atau 2.",
        "val.search_limit_bounds": "--search-limit harus antara 1 dan 100.",
        "val.file_mode": "--file hanya untuk --mode 1 atau 2.",
        "val.filename_requires_id": "--filename hanya berlaku untuk satu cerita (--id).",

        # ---------- search ----------
        "step.search": "Cari",
        "table.author": "Penulis",
        "search.none": "Tidak ada cerita ditemukan untuk '{query}'.",
        "status.searching": "Mencari '{query}'...",
        "err.select_invalid": "Indeks tidak valid: {error}",
        "search.page_info": "Halaman {page}/{total} ({start}-{end} dari {items})",
        "hint.search_page_nav": "Halaman berikutnya: n | sebelumnya: p",
        "prompt.search_mode": "Mode unduh (1 = 1 file gabungan, 2 = .zip per chapter)",
        "prompt.fanfic_indices": "Tambahkan indeks fanfic yang diunduh",
        "prompt.fanfic_indices_hint": "(contoh: 1-8,10)",
        "val.info_requires_id": "--info butuh --id.",
        "val.update_library_mode": "--update-library hanya untuk --mode 1 atau 2.",
        "val.watch_interval_min": "--watch-interval minimal 1 detik.",
        "val.username_invalid": "Nama pengguna Wattpad tidak valid: '{user}' (huruf, angka, '-', '_' saja).",

        # ---------- fitur library ----------
        "step.library": "Library",
        "step.update_library": "Update Library",
        "table.story_id": "ID Cerita",
        "hint.library_forget": "Hapus 1 cerita dari library: wattpdl --library-forget <id>",
        "ok.removed_from_library": "Dihapus dari library: {id}",
        "info.not_in_library": "Tidak ada cerita {id} di library.",
        "update.check_failed": "Gagal mengecek {title}: {error}",
        "update.all_up_to_date": "Semua {n} cerita tercatat sudah up to date. ({failed} gagal dicek)",
        "update.found": "Ditemukan {n} cerita dengan chapter baru.",
        "update.story_progress": "[{n}/{total}] {title}: {old} -> {new} chapter, mengunduh...",
        "update.done": "Selesai: {n} cerita diperbarui. ({failed} gagal dicek)",

        # ---------- --info ----------
        "info.status": "Status",
        "info.status_ongoing": "Ongoing",
        "info.status_completed": "Completed",
        "info.genre": "Genre",
        "info.description": "Deskripsi",

        # ---------- dry run ----------
        "dryrun.title": "Dry run (tidak ada file yang ditulis)",
        "dryrun.path": "Target file:",
        "dryrun.exists": "File sudah ada:",
        "dryrun.mode": "Mode:",
        "dryrun.chapters": "Chapter dipilih:",
        "dryrun.reused": "Akan dipakai dari progress sebelumnya:",
        "dryrun.to_download": "Akan diunduh:",

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
        "help.format": "Format file output. Bisa beberapa sekaligus: txt,docx,epub atau all (default: dari config tersimpan, atau txt).",
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
        "help.library": "Tampilkan semua cerita yang pernah diunduh penuh (tercatat di library).",
        "help.library_forget": "Hapus 1 cerita dari library (berhenti dipantau --check-updates/--update-library).",
        "help.update_library": (
            "Unduh ulang semua cerita di library yang punya chapter baru (mode 1/2). "
            "Isi file ditulis ulang seluruhnya; progress disimpan agar update berikutnya "
            "hanya mengunduh chapter yang baru."
        ),
        "help.json": "Untuk --library dan --check-updates: output JSON ke stdout.",
        "help.info": "Tampilkan detail cerita (--id) tanpa mengunduh apa pun.",
        "help.retries": "Jumlah percobaan ulang per chapter sebelum dilewati (default 3).",
        "help.timeout": "Timeout tiap request HTTP dalam detik (default 20).",
        "help.dry_run": "Simulasi: tampilkan file tujuan & jumlah chapter yang akan diunduh, tanpa menulis apa pun.",
        "help.search": "Cari cerita di Wattpad & tampilkan daftar (diberi nomor); unduh beberapa sekaligus dengan --select.",
        "help.search_limit": "Jumlah hasil --search yang diambil (default 40, maksimal 100).",
        "help.select": "Indeks cerita dari hasil --search, contoh: 1,3,5-8.",
        "help.file": "Unduh daftar cerita dari file (ID atau link per baris, '#' untuk komentar).",
        "help.filename": "Nama file output custom (hanya untuk satu cerita dengan --id, mis. --filename 'Seri Saya - Buku 1').",
        "step.file_batch": "Batch dari File",
        "warn.file_bad_line": "Baris dilewati (bukan ID/link cerita valid): {line}",
        "err.file_not_found": "File tidak ditemukan: {path}",
        "err.file_empty": "Tidak ada cerita valid di {path}",
        "file.story_failed": "[Gagal] {id}: {error}",
        "file.done": "Selesai: {n} cerita diunduh, {failed} gagal.",

        # ---------- wave 1: power tools ----------
        "help.report": "Tulis laporan unduhan ke PATH (.json atau .csv).",
        "help.config": "Tampilkan preferensi yang tersimpan.",
        "help.config_set": "Ubah preferensi, contoh: --config-set file_format=epub --config-set ui_lang=id.",
        "help.doctor": "Cek dependency, folder data, preferensi, dan konektivitas API.",
        "help.completion": "Cetak script shell completion (bash, zsh, fish, powershell).",
        "help.quiet": "Sembunyikan output normal (berguna untuk cron).",
        "help.verbose": "Tampilkan detail tambahan saat menjalankan.",
        "val.format_invalid": "Format tidak dikenal: {value}.",
        "val.config_set_format": "Gunakan format key=value: {item}",
        "val.config_set_key": "Kunci preferensi tidak dikenal: {name}",
        "val.config_set_value": "Nilai tidak valid untuk {name}: {value}",
        "val.report_ext": "Laporan harus berakhir dengan .json atau .csv.",
        "config.key": "Kunci",
        "config.value": "Nilai",
        "config.title": "Preferensi Tersimpan",
        "config.updated": "Preferensi diperbarui: {name} = {value}",
        "doctor.title": "Pemeriksaan Sistem",
        "doctor.python": "Versi Python",
        "doctor.deps": "Dependency",
        "doctor.config": "Preferensi",
        "doctor.dirs": "Folder data",
        "doctor.api": "Koneksi Wattpad API",
        "doctor.ok": "OK",
        "doctor.fail": "GAGAL",
        "report.written": "Laporan ditulis: {path}",
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
        "warn.parts_mismatch": (
            "⚠  Wattpad reports {reported} chapters, but only {accessible} are available. "
            "Some chapters may be hidden, paid, or unpublished, so they cannot be downloaded."
        ),
        "status.downloading_cover": "Downloading cover…",
        "info.images_downloaded": "🖼  {n} inline image(s) downloaded.",
        "warn.no_images": (
            "⚠  No inline images were downloaded from these chapters. "
            "If the story is image-based, the images may be unavailable or blocked by Wattpad."
        ),
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
        "api.context_chapter": "chapter",
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
        "val.retries_min": "--retries must be at least 1.",
        "val.retries_max": "--retries must be at most 10.",
        "val.timeout_min": "--timeout must be at least 1 second.",
        "val.json_requires": "--json only applies to --library and --check-updates.",
        "val.standalone_conflict": "Only one main command at a time (--library, --library-forget, --update-library, --check-updates, --search, --file, --config, --config-set, --doctor, --completion); it cannot be combined with --id/--user.",
        "val.select_requires_search": "--select requires --search.",
        "val.search_empty": "--search must not be empty.",
        "val.search_mode": "--search only supports --mode 1 or 2.",
        "val.search_limit_bounds": "--search-limit must be between 1 and 100.",
        "val.file_mode": "--file only supports --mode 1 or 2.",
        "val.filename_requires_id": "--filename only applies to a single story (--id).",

        # ---------- search ----------
        "step.search": "Search",
        "table.author": "Author",
        "search.none": "No stories found for '{query}'.",
        "status.searching": "Searching '{query}'...",
        "err.select_invalid": "Invalid selection: {error}",
        "search.page_info": "Page {page}/{total} ({start}-{end} of {items})",
        "hint.search_page_nav": "Next page: n | previous page: p",
        "prompt.search_mode": "Download mode (1 = 1 combined file, 2 = .zip per chapter)",
        "prompt.fanfic_indices": "Add indices of fanfics to download",
        "prompt.fanfic_indices_hint": "(example: 1-8,10)",
        "val.info_requires_id": "--info requires --id.",
        "val.update_library_mode": "--update-library only supports --mode 1 or 2.",
        "val.watch_interval_min": "--watch-interval must be at least 1 second.",
        "val.username_invalid": "Invalid Wattpad username: '{user}' (letters, digits, '-' and '_' only).",

        # ---------- library feature ----------
        "step.library": "Library",
        "step.update_library": "Update Library",
        "table.story_id": "Story ID",
        "hint.library_forget": "Remove one story from the library: wattpdl --library-forget <id>",
        "ok.removed_from_library": "Removed from the library: {id}",
        "info.not_in_library": "No story {id} in the library.",
        "update.check_failed": "Could not check {title}: {error}",
        "update.all_up_to_date": "All {n} recorded stories are up to date. ({failed} failed to check)",
        "update.found": "Found {n} stories with new chapters.",
        "update.story_progress": "[{n}/{total}] {title}: {old} -> {new} chapters, downloading...",
        "update.done": "Done: {n} stories updated. ({failed} failed to check)",

        # ---------- --info ----------
        "info.status": "Status",
        "info.status_ongoing": "Ongoing",
        "info.status_completed": "Completed",
        "info.genre": "Genre",
        "info.description": "Description",

        # ---------- dry run ----------
        "dryrun.title": "Dry run (no file will be written)",
        "dryrun.path": "Target file:",
        "dryrun.exists": "Target file already exists:",
        "dryrun.mode": "Mode:",
        "dryrun.chapters": "Chapters selected:",
        "dryrun.reused": "Reused from previous progress:",
        "dryrun.to_download": "To download:",

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
        "help.format": "Output file format. Accepts several at once: txt,docx,epub or all (default: saved config, or txt).",
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
        "help.library": "List every story that was fully downloaded before (recorded in the library).",
        "help.library_forget": "Remove one story from the library (stops --check-updates/--update-library tracking).",
        "help.update_library": (
            "Re-download every recorded story that has new chapters (mode 1/2). "
            "The file is rewritten in full; progress is kept so the next update "
            "only downloads the new chapters."
        ),
        "help.json": "With --library or --check-updates: print JSON to stdout.",
        "help.info": "Show the details of a story (--id) without downloading anything.",
        "help.retries": "Retries per chapter before it is skipped (default 3).",
        "help.timeout": "Timeout for every HTTP request in seconds (default 20).",
        "help.dry_run": "Simulate: show the target file and chapter counts without writing anything.",
        "help.search": "Search Wattpad stories & list them; download several at once with --select.",
        "help.search_limit": "How many --search results to fetch (default 40, max 100).",
        "help.select": "Story indices from the --search results, example: 1,3,5-8.",
        "help.file": "Download the story IDs/links listed in a file, one per line ('#' for comments).",
        "help.filename": "Custom output base name (only for a single story with --id, e.g. --filename 'My Series - Book 1').",
        "step.file_batch": "File Batch",
        "warn.file_bad_line": "Line skipped (not a valid story ID/link): {line}",
        "err.file_not_found": "File not found: {path}",
        "err.file_empty": "No valid stories in {path}",
        "file.story_failed": "[failed] {id}: {error}",
        "file.done": "Done: {n} stories downloaded, {failed} failed.",

        # ---------- wave 1: power tools ----------
        "help.report": "Write a download report to PATH (.json or .csv).",
        "help.config": "Show the saved preferences.",
        "help.config_set": "Change a preference, e.g. --config-set file_format=epub --config-set ui_lang=id.",
        "help.doctor": "Check dependencies, data folders, preferences and API connectivity.",
        "help.completion": "Print a shell completion script (bash, zsh, fish, powershell).",
        "help.quiet": "Hide normal output (useful for cron).",
        "help.verbose": "Show extra details while running.",
        "val.format_invalid": "Unknown format: {value}.",
        "val.config_set_format": "Use key=value form: {item}",
        "val.config_set_key": "Unknown preference key: {name}",
        "val.config_set_value": "Invalid value for {name}: {value}",
        "val.report_ext": "The report path must end with .json or .csv.",
        "config.key": "Key",
        "config.value": "Value",
        "config.title": "Saved Preferences",
        "config.updated": "Preference updated: {name} = {value}",
        "doctor.title": "System Check",
        "doctor.python": "Python version",
        "doctor.deps": "Dependencies",
        "doctor.config": "Preferences",
        "doctor.dirs": "Data folders",
        "doctor.api": "Wattpad API connection",
        "doctor.ok": "OK",
        "doctor.fail": "FAIL",
        "report.written": "Report written: {path}",
    },
}
