"""
WattPDL — Wattpad Story Downloader
Entry point utama. Dua mode:
  - Interaktif  : python wattpdl.py           (tanpa argumen, tanya-jawab di terminal)
  - Non-interaktif : python wattpdl.py --id ... --mode ... (untuk scripting/otomatisasi)
Alur: ambil input (prompt atau argumen) -> fetch data (api.py) -> tulis file
(writers.py) -> tampilkan progres (cli.py). Preferensi tersimpan lewat
config.py, dan progress unduhan lewat progress.py untuk fitur resume.
"""
import pathlib
import sys
import time

import requests
from rich import box
from rich.align import Align
from rich.panel import Panel
from rich.table import Table

from . import api, cli, cli_args, library, metacache, updater, writers
from . import config as config_mod
from . import progress as progress_mod
from .cli import console, step_rule


def resolve_save_dir(custom_path: str, config: dict) -> pathlib.Path:
    """Tentukan folder simpan: argumen/input custom > config tersimpan > folder Downloads default."""
    if custom_path:
        save_dir = pathlib.Path(custom_path).expanduser().resolve()
    elif config.get("save_dir"):
        save_dir = pathlib.Path(config["save_dir"])
    else:
        save_dir = cli.get_default_download_dir()

    try:
        save_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        console.print(f"[danger]❌  Folder tidak bisa dibuat:[/danger] {e}")
        try:
            fallback = cli.get_default_download_dir()
        except OSError as e2:
            console.print(f"[danger]❌  Folder default juga tidak bisa dibuat:[/danger] {e2}")
            console.print("    [muted]Coba jalankan ulang dengan folder simpan lain yang kamu punya izin tulis di sana.[/muted]")
            sys.exit(1)
        console.print(f"    [muted]Menggunakan folder default: {fallback}[/muted]")
        save_dir = fallback
    return save_dir


def should_skip_existing(full_path: pathlib.Path, skip_existing: bool) -> bool:
    """True kalau file output sudah ada dan mode skip-existing aktif —
    dipakai mode non-interaktif supaya tidak menimpa/mengunduh ulang tanpa perlu.
    Dipisah jadi fungsi murni supaya gampang ditest tanpa perlu mock filesystem penuh."""
    return skip_existing and full_path.exists()


def resolve_chapters(mode: str, parts: list, chapters_arg: str = None, chapter_arg: int = None) -> list:
    """Tentukan chapter yang diunduh, dari argumen (non-interaktif) atau prompt (interaktif)."""
    if mode == "3":
        if chapters_arg is not None:
            numbers = cli.parse_chapter_selection(chapters_arg, len(parts))
            console.print(f"[success]✔ {len(numbers)} chapter dipilih.[/success]")
            return [(n, parts[n - 1]) for n in numbers]
        return cli.select_multiple_chapters(parts)

    if mode == "4":
        if chapter_arg is not None:
            n = chapter_arg
            if not (1 <= n <= len(parts)):
                console.print(f"[danger]❌  Chapter {n} di luar rentang (1-{len(parts)}).[/danger]")
                sys.exit(1)
            part = parts[n - 1]
            console.print(f"[success]✔ Dipilih:[/success] Chapter {n} — {part.get('title', '')}")
            return [(n, part)]
        return [cli.select_single_chapter(parts)]

    return list(enumerate(parts, start=1))


def run_download(story_id, title, author, parts, mode, file_format, save_dir,
                  chapters_arg=None, chapter_arg=None, meta=None, cover_bytes=None,
                  skip_existing=False, interactive=False, workers=1, include_images=False):
    """Alur unduh bersama untuk mode interaktif maupun non-interaktif."""
    indexed_parts = resolve_chapters(mode, parts, chapters_arg, chapter_arg)

    ext = {"2": "docx", "3": "epub", "4": "md", "5": "pdf"}.get(file_format, "txt")
    base_name = writers.safe_filename(title)

    if mode == "1":
        full_path = save_dir / f"{base_name}.{ext}"
    elif mode == "2":
        full_path = save_dir / f"{base_name}.zip"
    elif mode == "3":
        full_path = save_dir / f"{base_name}_pilihan.{ext}"
    else:
        chap_no, chap_part = indexed_parts[0]
        chap_title = writers.safe_filename(chap_part.get("title", f"Chapter {chap_no}"))
        full_path = save_dir / f"{base_name}_Ch{chap_no:03d}_{chap_title}.{ext}"

    try:
        path_exists = full_path.exists()
    except OSError as e:
        # Bisa kejadian kalau nama file gabungan (judul cerita + judul chapter
        # untuk mode 4, atau folder tujuan yang dipilih user sudah panjang)
        # tetap melebihi batas panjang path sistem operasi walau sudah dipotong
        # oleh safe_filename(). Tampilkan pesan rapi, jangan biarkan traceback mentah.
        console.print(f"\n[danger]❌  Nama file/path tidak valid atau terlalu panjang:[/danger] {e}")
        console.print(f"    [muted]Path yang dicoba: {full_path}[/muted]")
        console.print("    [muted]Coba pilih folder simpan dengan path yang lebih pendek.[/muted]")
        sys.exit(1)

    if path_exists:
        if interactive:
            if not cli.confirm_overwrite(full_path):
                console.print("[muted]Dilewati — file yang sudah ada tidak diubah.[/muted]\n")
                return
        elif should_skip_existing(full_path, skip_existing):
            console.print(
                f"[muted]⏭  Dilewati — file sudah ada:[/muted] [accent]{full_path}[/accent]\n"
                "    [muted](hapus --skip-existing kalau mau menimpanya)[/muted]"
            )
            return

    console.print(f"\n[value]💾 File akan disimpan di:[/value] [accent]{full_path}[/accent]")

    step_rule("Mengunduh Chapter")
    start_time = time.time()
    rate_limiter = api.AdaptiveRateLimiter()
    results, failed_chapters, images_by_idx = cli.download_chapters(
        indexed_parts, story_id=story_id, max_workers=workers,
        rate_limiter=rate_limiter, include_images=include_images,
    )
    elapsed = cli.format_duration(time.time() - start_time)

    try:
        if mode == "2":
            if file_format == "2":
                writers.write_separate_docx_zip(full_path, title, author, story_id, results,
                                                 meta=meta, cover_bytes=cover_bytes, images_by_idx=images_by_idx)
            elif file_format == "3":
                writers.write_separate_epub_zip(full_path, title, author, story_id, results,
                                                 meta=meta, cover_bytes=cover_bytes, images_by_idx=images_by_idx)
            elif file_format == "4":
                writers.write_separate_md_zip(full_path, title, author, story_id, results, meta=meta)
            elif file_format == "5":
                writers.write_separate_pdf_zip(full_path, title, author, story_id, results,
                                                meta=meta, cover_bytes=cover_bytes, images_by_idx=images_by_idx)
            else:
                writers.write_separate_zip(full_path, title, author, story_id, results)
        else:
            if file_format == "2":
                writers.write_combined_docx(full_path, title, author, story_id, results,
                                             meta=meta, cover_bytes=cover_bytes, images_by_idx=images_by_idx)
            elif file_format == "3":
                writers.write_combined_epub(full_path, title, author, story_id, results,
                                             meta=meta, cover_bytes=cover_bytes, images_by_idx=images_by_idx)
            elif file_format == "4":
                writers.write_combined_md(full_path, title, author, story_id, results, meta=meta)
            elif file_format == "5":
                writers.write_combined_pdf(full_path, title, author, story_id, results,
                                            meta=meta, cover_bytes=cover_bytes, images_by_idx=images_by_idx)
            else:
                writers.write_combined_txt(full_path, title, author, story_id, results)
    except OSError as e:
        # Chapter sudah terlanjur diunduh (dan progress-nya sudah tersimpan lewat
        # progress.py) — jangan sampai kegagalan MENULIS file di detik terakhir
        # (path terlalu panjang, disk penuh, tidak ada izin tulis, dst.) muncul
        # sebagai traceback mentah. Beri tahu user progress tidak hilang.
        console.print(f"\n[danger]❌  Gagal menulis file output:[/danger] {e}")
        console.print(f"    [muted]Path yang dicoba: {full_path}[/muted]")
        console.print(
            "    [muted]Chapter yang sudah berhasil diunduh tetap tersimpan di progress — "
            "jalankan ulang setelah masalah di atas diperbaiki.[/muted]"
        )
        sys.exit(1)

    step_rule("Ringkasan")
    summary = Table(show_header=False, box=box.SIMPLE, padding=(0, 1), expand=False)
    summary.add_column(style="muted")
    summary.add_column(style="value")
    summary.add_row("📁 File tersimpan di", f"[accent]{full_path}[/accent]")
    summary.add_row("✅ Berhasil", f"[success]{len(results) - len(failed_chapters)}/{len(results)}[/success]")
    if failed_chapters:
        summary.add_row("⚠️  Gagal", f"[danger]{len(failed_chapters)}[/danger]")
    summary.add_row("⏱️  Waktu total", elapsed)

    if failed_chapters:
        fail_list = "\n".join(f"[danger]• {ch}[/danger]" for ch in failed_chapters)
        body = Table.grid(padding=(0, 0))
        body.add_row(summary)
        body.add_row("")
        body.add_row(f"[muted]Chapter yang gagal:[/muted]\n{fail_list}")
        console.print(Panel(
            body,
            title="[warning]⚠️  Selesai dengan beberapa kegagalan[/warning]",
            border_style="warning",
            box=box.ROUNDED,
            padding=(1, 2),
        ))
        console.print(
            "[muted]Progress chapter yang sudah berhasil sudah tersimpan — "
            "jalankan ulang cerita yang sama untuk melanjutkan tanpa mengulang dari awal.[/muted]\n"
        )
    else:
        # Semua chapter berhasil -> file progress resume cerita ini tidak diperlukan lagi.
        progress_mod.clear_progress(story_id)
        if mode in ("1", "2"):
            # Catat ke library supaya --check-updates / --watch bisa mendeteksi
            # kalau nanti ada chapter baru di cerita ini.
            library.remember_story(story_id, title, len(parts))
        console.print(Panel(
            summary,
            title="[success]🎉 Berhasil!  Semua chapter tersimpan[/success]",
            border_style="success",
            box=box.DOUBLE,
            padding=(1, 2),
        ))
        console.print()

    # simpan preferensi format & folder simpan untuk sesi berikutnya
    config_mod.save_config(save_dir=str(save_dir), file_format=file_format)


def fetch_story_or_exit(story_id: str, use_cache: bool = True):
    if use_cache:
        cached = metacache.get_cached_story(story_id)
        if cached:
            return cached

    with console.status(f"[accent]Mengambil info cerita (ID: {story_id})…[/accent]", spinner="dots"):
        try:
            title, author, parts, meta = api.get_story_info(story_id)
        except (api.StoryNotFoundError, api.StoryAccessError) as e:
            # Pesan sudah spesifik dari api.py (bedain 404 vs 403/401), tampilkan apa adanya.
            console.print(f"[danger]❌  {e}[/danger]")
            sys.exit(1)
        except requests.RequestException as e:
            console.print(f"[danger]❌  Gagal mengakses API Wattpad:[/danger] {e}")
            console.print("    [muted]Pastikan koneksi internet stabil, dan coba lagi beberapa saat.[/muted]")
            sys.exit(1)

    if not parts:
        console.print("[danger]❌  Tidak ada chapter ditemukan. Cek lagi ID/link ceritanya.[/danger]")
        sys.exit(1)

    if use_cache:
        metacache.save_story_cache(story_id, title, author, parts, meta)
    return title, author, parts, meta


def run_non_interactive(args):
    cli.reset_steps()
    try:
        cli_args.validate_non_interactive_args(args)
    except ValueError as e:
        console.print(f"[danger]❌  {e}[/danger]")
        sys.exit(1)

    try:
        story_id = api.extract_story_id(args.id)
    except ValueError as e:
        console.print(f"[danger]❌  {e}[/danger]")
        sys.exit(1)

    config = config_mod.load_config()
    title, author, parts, meta = fetch_story_or_exit(story_id, use_cache=not args.no_cache)

    step_rule("Info Cerita")
    info_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1), expand=False)
    info_table.add_column(style="muted")
    info_table.add_column(style="value")
    info_table.add_row("📌 Judul", title)
    info_table.add_row("✍️  Penulis", author)
    info_table.add_row("📚 Jumlah chapter", str(len(parts)))
    console.print(Panel(info_table, border_style="success", box=box.ROUNDED, padding=(1, 2)))

    file_format = cli_args.FORMAT_TO_CODE[args.format] if args.format else config.get("file_format", "1")
    if file_format == "2":
        writers.check_docx_available(console)
    elif file_format == "3":
        writers.check_epub_available(console)
    elif file_format == "5":
        writers.check_pdf_available(console)

    save_dir = resolve_save_dir(args.output_dir, config)

    cover_bytes = None
    if not args.no_cover and file_format in ("2", "3", "5") and meta.get("cover_url"):
        cover_bytes = api.download_cover_image(meta["cover_url"])

    run_download(
        story_id, title, author, parts, args.mode, file_format, save_dir,
        chapters_arg=args.chapters, chapter_arg=args.chapter,
        meta=meta, cover_bytes=cover_bytes, skip_existing=args.skip_existing,
        workers=args.workers, include_images=args.include_images,
    )


def run_interactive():
    cli.reset_steps()
    console.print()
    console.print(Align.center(cli.LOGO))
    console.print(
        Align.center(
            "[value]📖 Wattpad Story Downloader[/value]  [muted]—  simpan cerita jadi file .txt/.docx offline[/muted]"
        )
    )

    config = config_mod.load_config()

    step_rule("Masukkan Cerita")
    raw = cli.Prompt.ask("[value]Link atau ID cerita Wattpad[/value]")
    try:
        story_id = api.extract_story_id(raw)
    except ValueError as e:
        console.print(f"\n[danger]❌  {e}[/danger]")
        sys.exit(1)

    title, author, parts, meta = fetch_story_or_exit(story_id)

    step_rule("Info Cerita")
    info_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1), expand=False)
    info_table.add_column(style="muted")
    info_table.add_column(style="value")
    info_table.add_row("📌 Judul", title)
    info_table.add_row("✍️  Penulis", author)
    info_table.add_row("📚 Jumlah chapter", str(len(parts)))
    console.print(Panel(info_table, border_style="success", box=box.ROUNDED, padding=(1, 2)))

    step_rule("Pilih Mode Unduh")
    mode_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1), expand=False)
    mode_table.add_column(style="accent", justify="right")
    mode_table.add_column(style="value")
    mode_table.add_row("1", "Semua chapter → 1 file gabungan")
    mode_table.add_row("2", "Semua chapter → file terpisah per chapter, dikemas .zip")
    mode_table.add_row("3", "Pilih beberapa chapter → 1 file gabungan")
    mode_table.add_row("4", "Pilih 1 chapter saja")
    console.print(mode_table)

    mode = cli.Prompt.ask("\n[value]Pilih mode[/value]", choices=["1", "2", "3", "4"], default="1")

    format_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1), expand=False)
    format_table.add_column(style="accent", justify="right")
    format_table.add_column(style="value")
    format_table.add_row("1", "Teks polos (.txt)")
    format_table.add_row("2", "Dokumen Word (.docx)")
    format_table.add_row("3", "Ebook (.epub)")
    format_table.add_row("4", "Markdown (.md)")
    format_table.add_row("5", "PDF (.pdf)")
    console.print()
    console.print(format_table)

    file_format = cli.Prompt.ask(
        "\n[value]Pilih format file[/value]",
        choices=["1", "2", "3", "4", "5"],
        default=config.get("file_format", "1"),
    )
    if file_format == "2":
        writers.check_docx_available(console)
    elif file_format == "3":
        writers.check_epub_available(console)
    elif file_format == "5":
        writers.check_pdf_available(console)

    cover_bytes = None
    if file_format in ("2", "3", "5") and meta.get("cover_url"):
        cover_bytes = api.download_cover_image(meta["cover_url"])

    step_rule("Folder Penyimpanan")
    default_dir = pathlib.Path(config["save_dir"]) if config.get("save_dir") else cli.get_default_download_dir()
    console.print(f"[muted]Folder default:[/muted] [accent]{default_dir}[/accent]")
    custom = cli.Prompt.ask(
        "[muted]Tekan Enter untuk pakai folder itu, atau ketik path lain[/muted]",
        default="",
        show_default=False,
    ).strip()
    save_dir = resolve_save_dir(custom, config)

    run_download(story_id, title, author, parts, mode, file_format, save_dir,
                 meta=meta, cover_bytes=cover_bytes, interactive=True)


def run_user_mode(args) -> None:
    """Unduh semua/cerita pilihan dari satu penulis Wattpad sekaligus (--user).
    Selalu non-interaktif: cerita mana yang diunduh ditentukan lewat --user-select,
    dan tiap cerita diunduh mode 1 (gabungan) atau 2 (zip terpisah) — mode 3/4
    (pilih chapter tertentu) tidak relevan untuk banyak cerita sekaligus.
    """
    cli.reset_steps()
    mode = args.mode or "1"
    if mode not in ("1", "2"):
        console.print("[danger]❌  --user hanya mendukung --mode 1 atau 2 (unduh chapter tertentu tidak berlaku untuk banyak cerita sekaligus).[/danger]")
        sys.exit(1)

    step_rule(f"Daftar Cerita — {args.user}")
    try:
        with console.status(f"[accent]Mengambil daftar cerita milik '{args.user}'…[/accent]", spinner="dots"):
            stories = api.get_author_stories(args.user)
    except (api.StoryNotFoundError, api.StoryAccessError) as e:
        console.print(f"[danger]❌  {e}[/danger]")
        sys.exit(1)
    except requests.RequestException as e:
        console.print(f"[danger]❌  Gagal mengakses API Wattpad:[/danger] {e}")
        sys.exit(1)

    if not stories:
        console.print(f"[danger]❌  Tidak ada cerita ditemukan untuk penulis '{args.user}'.[/danger]")
        sys.exit(1)

    table = Table(box=box.SIMPLE_HEAD, padding=(0, 1), expand=False)
    table.add_column("No", style="muted", justify="right", width=5)
    table.add_column("Judul", style="value")
    table.add_column("Chapter", style="muted", justify="right")
    for i, s in enumerate(stories, start=1):
        table.add_row(str(i), s["title"], str(s["num_parts"]))
    console.print(table)

    if args.user_select.strip().lower() == "all":
        chosen_indices = list(range(1, len(stories) + 1))
    else:
        try:
            chosen_indices = cli.parse_chapter_selection(args.user_select, len(stories))
        except ValueError as e:
            console.print(f"[danger]❌  --user-select tidak valid: {e}[/danger]")
            sys.exit(1)

    console.print(f"\n[success]✔ {len(chosen_indices)} dari {len(stories)} cerita akan diunduh.[/success]")

    config = config_mod.load_config()
    file_format = cli_args.FORMAT_TO_CODE[args.format] if args.format else config.get("file_format", "1")
    if file_format == "2":
        writers.check_docx_available(console)
    elif file_format == "3":
        writers.check_epub_available(console)
    elif file_format == "5":
        writers.check_pdf_available(console)
    save_dir = resolve_save_dir(args.output_dir, config)

    for n, story_index in enumerate(chosen_indices, start=1):
        story_summary = stories[story_index - 1]
        console.print(f"\n[primary]— Cerita {n}/{len(chosen_indices)}: {story_summary['title']} —[/primary]")
        title, author, parts, meta = fetch_story_or_exit(story_summary["id"], use_cache=not args.no_cache)

        cover_bytes = None
        if not args.no_cover and file_format in ("2", "3", "5") and meta.get("cover_url"):
            cover_bytes = api.download_cover_image(meta["cover_url"])

        run_download(
            story_summary["id"], title, author, parts, mode, file_format, save_dir,
            meta=meta, cover_bytes=cover_bytes, skip_existing=args.skip_existing,
            workers=args.workers, include_images=args.include_images,
        )

    config_mod.save_config(save_dir=str(save_dir), file_format=file_format)


def run_check_updates() -> None:
    """Cek semua cerita yang pernah diunduh penuh (tercatat di library.json)
    apakah ada chapter baru di Wattpad sekarang. Tidak mengunduh apa pun,
    cuma melaporkan — user tinggal jalankan ulang unduhan normal kalau ada
    yang mau di-update.
    """
    cli.reset_steps()
    step_rule("Cek Update Cerita")
    saved = library.load_library()
    if not saved:
        console.print(
            "[muted]Belum ada cerita yang tercatat. Cerita otomatis tercatat setelah "
            "berhasil diunduh penuh lewat mode 1 atau 2.[/muted]"
        )
        return

    table = Table(box=box.SIMPLE_HEAD, padding=(0, 1), expand=False)
    table.add_column("Judul", style="value")
    table.add_column("Chapter Tercatat", style="muted", justify="right")
    table.add_column("Chapter Sekarang", style="muted", justify="right")
    table.add_column("Status", style="value")

    any_update = False
    for story_id, entry in saved.items():
        old_count = entry.get("num_parts", 0)
        try:
            _, _, parts, _ = api.get_story_info(story_id)
            new_count = len(parts)
        except api.StoryNotFoundError:
            table.add_row(entry.get("title", story_id), str(old_count), "-", "[danger]❌ dihapus/tidak ditemukan[/danger]")
            continue
        except (api.StoryAccessError, requests.RequestException):
            table.add_row(entry.get("title", story_id), str(old_count), "?", "[warning]⚠ gagal cek[/warning]")
            continue

        if new_count > old_count:
            any_update = True
            status = f"[success]✨ +{new_count - old_count} chapter baru[/success]"
        else:
            status = "[muted]sudah terbaru[/muted]"
        table.add_row(entry.get("title", story_id), str(old_count), str(new_count), status)

    console.print(table)
    if any_update:
        console.print(
            "\n[muted]Ada cerita dengan chapter baru — jalankan ulang unduhan normal "
            "(mode 1/2) untuk cerita itu untuk memperbarui filenya.[/muted]"
        )


def run_watch(args) -> None:
    """Pantau 1 cerita terus-menerus (--watch), otomatis unduh ulang penuh
    begitu jumlah chapter bertambah. Cocok untuk cerita ongoing yang rutin
    update. Berhenti dengan Ctrl+C, atau otomatis berhenti setelah
    --watch-max-iterations kali cek (dipakai untuk testing, biasanya tidak diisi
    oleh user sehingga berjalan tanpa batas)."""
    cli.reset_steps()
    try:
        cli_args.validate_non_interactive_args(args)
    except ValueError as e:
        console.print(f"[danger]❌  {e}[/danger]")
        sys.exit(1)
    try:
        story_id = api.extract_story_id(args.id)
    except ValueError as e:
        console.print(f"[danger]❌  {e}[/danger]")
        sys.exit(1)

    console.print(
        f"\n[value]👀 Mode watch aktif[/value] untuk cerita ID [accent]{story_id}[/accent]. "
        f"Cek tiap [accent]{args.watch_interval}[/accent] detik. [muted]Tekan Ctrl+C untuk berhenti.[/muted]\n"
    )

    iteration = 0
    last_known_parts = None
    try:
        while True:
            iteration += 1
            try:
                title, author, parts, meta = api.get_story_info(story_id)
            except (api.StoryNotFoundError, api.StoryAccessError) as e:
                console.print(f"[danger]❌  {e}[/danger]")
                sys.exit(1)
            except requests.RequestException as e:
                console.print(f"[warning]⚠  Gagal cek update (percobaan #{iteration}): {e}[/warning]")
                parts = None

            if parts is not None and (last_known_parts is None or len(parts) > last_known_parts):
                if last_known_parts is not None:
                    console.print(
                        f"\n[success]✨ Chapter baru terdeteksi![/success] "
                        f"({last_known_parts} → {len(parts)} chapter). Mengunduh ulang…"
                    )
                config = config_mod.load_config()
                file_format = cli_args.FORMAT_TO_CODE[args.format] if args.format else config.get("file_format", "1")
                if file_format == "2":
                    writers.check_docx_available(console)
                elif file_format == "3":
                    writers.check_epub_available(console)
                elif file_format == "5":
                    writers.check_pdf_available(console)
                save_dir = resolve_save_dir(args.output_dir, config)
                cover_bytes = None
                if not args.no_cover and file_format in ("2", "3", "5") and meta.get("cover_url"):
                    cover_bytes = api.download_cover_image(meta["cover_url"])
                run_download(
                    story_id, title, author, parts, args.mode, file_format, save_dir,
                    chapters_arg=args.chapters, chapter_arg=args.chapter,
                    meta=meta, cover_bytes=cover_bytes, skip_existing=False,
                    workers=args.workers, include_images=args.include_images,
                )
                last_known_parts = len(parts)
            elif parts is not None:
                console.print(
                    f"[muted]↻ Belum ada chapter baru ({len(parts)} chapter). "
                    f"Cek lagi dalam {args.watch_interval} detik…[/muted]"
                )

            if args.watch_max_iterations is not None and iteration >= args.watch_max_iterations:
                console.print("[muted]Batas jumlah pengecekan tercapai, mode watch berhenti.[/muted]")
                break
            time.sleep(args.watch_interval)
    except KeyboardInterrupt:
        console.print("\n[muted]Mode watch dihentikan.[/muted]")


def main():
    args = cli_args.parse_args()

    if not args.no_update_check:
        try:
            latest = updater.check_for_update()
            if latest:
                console.print(
                    f"[muted]💡 Versi baru wattpdl tersedia: {latest}. "
                    f"Update dengan:[/muted] [accent]pip install --upgrade wattpdl[/accent]\n"
                )
        except Exception:
            pass  # cek update tidak boleh pernah menghentikan aplikasi utama

    if args.check_updates:
        run_check_updates()
    elif args.user:
        run_user_mode(args)
    elif args.id:
        if args.watch:
            run_watch(args)
        else:
            run_non_interactive(args)
    else:
        run_interactive()


if __name__ == "__main__":
    main()
