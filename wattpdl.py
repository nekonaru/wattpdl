"""
WattPDL — Wattpad Story Downloader
Entry point utama. Alur program: ambil input user -> fetch data (api.py)
-> tulis file (writers.py) -> tampilkan progres (cli.py).
"""
import pathlib
import sys
import time

import requests
from rich import box
from rich.align import Align
from rich.panel import Panel
from rich.table import Table

import api
import cli
import writers
from cli import console, step_rule


def main():
    console.print()
    console.print(Align.center(cli.LOGO))
    console.print(
        Align.center(
            "[value]📖 Wattpad Story Downloader[/value]  [muted]—  simpan cerita jadi file .txt/.docx offline[/muted]"
        )
    )

    step_rule("Masukkan Cerita")
    raw = cli.Prompt.ask("[value]Link atau ID cerita Wattpad[/value]")
    try:
        story_id = api.extract_story_id(raw)
    except ValueError as e:
        console.print(f"\n[danger]❌  {e}[/danger]")
        sys.exit(1)

    with console.status(f"[accent]Mengambil info cerita (ID: {story_id})…[/accent]", spinner="dots"):
        try:
            title, author, parts = api.get_story_info(story_id)
        except requests.HTTPError as e:
            console.print(f"[danger]❌  Gagal mengakses API Wattpad:[/danger] {e}")
            console.print("    [muted]Pastikan ID/link benar dan cerita tidak di-private.[/muted]")
            sys.exit(1)

    if not parts:
        console.print("[danger]❌  Tidak ada chapter ditemukan. Cek lagi ID/link ceritanya.[/danger]")
        sys.exit(1)

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

    mode = cli.Prompt.ask(
        "\n[value]Pilih mode[/value]",
        choices=["1", "2", "3", "4"],
        default="1",
    )

    format_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1), expand=False)
    format_table.add_column(style="accent", justify="right")
    format_table.add_column(style="value")
    format_table.add_row("1", "Teks polos (.txt)")
    format_table.add_row("2", "Dokumen Word (.docx)")
    console.print()
    console.print(format_table)

    file_format = cli.Prompt.ask(
        "\n[value]Pilih format file[/value]",
        choices=["1", "2"],
        default="1",
    )
    if file_format == "2":
        writers.check_docx_available(console)

    if mode == "3":
        indexed_parts = cli.select_multiple_chapters(parts)
    elif mode == "4":
        chosen = cli.select_single_chapter(parts)
        indexed_parts = [chosen]
    else:
        indexed_parts = list(enumerate(parts, start=1))

    step_rule("Folder Penyimpanan")
    default_dir = cli.get_default_download_dir()
    console.print(f"[muted]Folder default:[/muted] [accent]{default_dir}[/accent]")
    custom = cli.Prompt.ask(
        "[muted]Tekan Enter untuk pakai folder itu, atau ketik path lain[/muted]",
        default="",
        show_default=False,
    ).strip()

    if custom:
        save_dir = pathlib.Path(custom).expanduser().resolve()
        try:
            save_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            console.print(f"[danger]❌  Folder tidak bisa dibuat:[/danger] {e}")
            console.print(f"    [muted]Menggunakan folder default: {default_dir}[/muted]")
            save_dir = default_dir
    else:
        save_dir = default_dir

    ext = "docx" if file_format == "2" else "txt"
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

    console.print(f"\n[value]💾 File akan disimpan di:[/value] [accent]{full_path}[/accent]")

    step_rule("Mengunduh Chapter")
    start_time = time.time()
    results, failed_chapters = cli.download_chapters(indexed_parts)
    elapsed = cli.format_duration(time.time() - start_time)

    if mode == "2":
        if file_format == "2":
            writers.write_separate_docx_zip(full_path, title, author, story_id, results)
        else:
            writers.write_separate_zip(full_path, title, author, story_id, results)
    else:
        if file_format == "2":
            writers.write_combined_docx(full_path, title, author, story_id, results)
        else:
            writers.write_combined_txt(full_path, title, author, story_id, results)

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
        console.print("[muted]Jalankan ulang script untuk mencoba mengunduh ulang chapter yang gagal.[/muted]\n")
    else:
        console.print(Panel(
            summary,
            title="[success]🎉 Berhasil!  Semua chapter tersimpan[/success]",
            border_style="success",
            box=box.DOUBLE,
            padding=(1, 2),
        ))
        console.print()


if __name__ == "__main__":
    main()
