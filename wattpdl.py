import os
import re
import sys
import time
import pathlib
import requests

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.prompt import Prompt
from rich import box

console = Console()
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

DELAY_SECONDS = 0.5   
MAX_RETRIES   = 3    

def get_default_download_dir() -> pathlib.Path:
    """
    Kembalikan folder Downloads bawaan sistem operasi:
      - Windows : C:\\Users\\<user>\\Downloads
      - macOS   : /Users/<user>/Downloads
      - Linux   : /home/<user>/Downloads  (atau XDG_DOWNLOAD_DIR)
    """
    xdg = os.environ.get("XDG_DOWNLOAD_DIR", "").strip()
    if xdg and pathlib.Path(xdg).is_dir():
        return pathlib.Path(xdg)

    downloads = pathlib.Path.home() / "Downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    return downloads

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
            console.print(
                f"    [yellow]⚠  Gagal (percobaan {attempt}/{retries}), "
                f"coba lagi dalam {wait}s… ({e})[/yellow]"
            )
            time.sleep(wait)
    return ""  

def html_to_text(html: str) -> str:
    """Konversi HTML Wattpad ke teks bersih."""
    text = re.sub(r"</p>",       "\n\n", html, flags=re.IGNORECASE)
    text = re.sub(r"<br\s*/?>",  "\n",   text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>",   "",     text)
    text = re.sub(r"\n{3,}",    "\n\n", text)
    return text.strip()


def safe_filename(name: str) -> str:
    """Buat nama file yang aman untuk semua sistem operasi."""
    name = re.sub(r'[<>:"/\\|?*]', "", name)
    name = re.sub(r"[^\w\s\-]", "", name).strip()
    name = re.sub(r"\s+", "_", name)
    return name or "cerita_wattpad"

def main():
    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]WATTPAD DOWNLOADER[/bold cyan]\n"
            "[dim]Simpan cerita favoritmu ke file .txt[/dim]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 4),
        )
    )

    raw = Prompt.ask("\n[bold]Masukkan link atau ID cerita Wattpad[/bold]")
    try:
        story_id = extract_story_id(raw)
    except ValueError as e:
        console.print(f"\n[bold red]❌  {e}[/bold red]")
        sys.exit(1)

    with console.status(f"[cyan]Mengambil info cerita (ID: {story_id})…[/cyan]"):
        try:
            title, author, parts = get_story_info(story_id)
        except requests.HTTPError as e:
            console.print(f"[bold red]❌  Gagal mengakses API Wattpad:[/bold red] {e}")
            console.print("    [dim]Pastikan ID/link benar dan cerita tidak di-private.[/dim]")
            sys.exit(1)

    if not parts:
        console.print("[bold red]❌  Tidak ada chapter ditemukan. Cek lagi ID/link ceritanya.[/bold red]")
        sys.exit(1)

    info_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
    info_table.add_column(style="dim")
    info_table.add_column(style="bold white")
    info_table.add_row("Judul", title)
    info_table.add_row("Penulis", author)
    info_table.add_row("Jumlah chapter", str(len(parts)))
    console.print()
    console.print(Panel(info_table, title="📖 Info Cerita", border_style="green", box=box.ROUNDED))
    default_dir = get_default_download_dir()
    console.print(f"\n[dim]Folder default penyimpanan:[/dim] {default_dir}")
    custom = Prompt.ask(
        "Tekan Enter untuk memakai folder itu, atau ketik path lain",
        default="",
        show_default=False,
    ).strip()

    if custom:
        save_dir = pathlib.Path(custom).expanduser().resolve()
        try:
            save_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            console.print(f"[bold red]❌  Folder tidak bisa dibuat:[/bold red] {e}")
            console.print(f"    [dim]Menggunakan folder default: {default_dir}[/dim]")
            save_dir = default_dir
    else:
        save_dir = default_dir

    filename  = f"{safe_filename(title)}.txt"
    full_path = save_dir / filename

    console.print(f"\n[bold]💾 File akan disimpan di:[/bold] [cyan]{full_path}[/cyan]\n")
    failed_chapters: list[str] = []

    progress_columns = [
        SpinnerColumn(style="cyan"),
        TextColumn("[bold cyan]{task.description}[/bold cyan]"),
        BarColumn(bar_width=30, complete_style="green", finished_style="green"),
        TextColumn("[progress.percentage]{task.percentage:>5.1f}%"),
        TextColumn("[dim]{task.completed}/{task.total}[/dim]"),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
    ]

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(f"{title}\n")
        f.write(f"oleh {author}\n")
        f.write(f"Sumber : https://www.wattpad.com/story/{story_id}\n")
        f.write(f"\n{'=' * 50}\n\n")

        with Progress(*progress_columns, console=console) as progress:
            task = progress.add_task("Mengunduh", total=len(parts))

            for i, part in enumerate(parts, start=1):
                part_id       = part["id"]
                chapter_title = part.get("title", f"Chapter {i}")

                short_title = (chapter_title[:28] + "…") if len(chapter_title) > 28 else chapter_title
                progress.update(task, description=f"{short_title:<30}")

                try:
                    html = get_chapter_html(part_id)
                    text = html_to_text(html)
                except Exception as e:
                    console.print(f"\n    [bold red]⚠  Chapter [{i}] gagal:[/bold red] {e}")
                    text = "[GAGAL DIUNDUH — coba jalankan ulang]"
                    failed_chapters.append(f"Chapter {i}: {chapter_title}")

                f.write(f"\n\n{'#' * 5} {chapter_title} {'#' * 5}\n\n")
                f.write(text)
                f.write("\n")

                progress.advance(task)
                time.sleep(DELAY_SECONDS)

    console.print()
    if failed_chapters:
        summary = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
        summary.add_column(style="dim")
        summary.add_column()
        summary.add_row("File tersimpan di", f"[cyan]{full_path}[/cyan]")
        summary.add_row("Berhasil", f"[green]{len(parts) - len(failed_chapters)}/{len(parts)}[/green]")
        summary.add_row("Gagal", f"[red]{len(failed_chapters)}[/red]")
        for ch in failed_chapters:
            summary.add_row("", f"[red]• {ch}[/red]")
        console.print(Panel(summary, title="⚠️  Selesai dengan beberapa kegagalan",
                             border_style="yellow", box=box.ROUNDED))
        console.print("[dim]Jalankan ulang script untuk mencoba mengunduh ulang chapter yang gagal.[/dim]\n")
    else:
        summary = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
        summary.add_column(style="dim")
        summary.add_column()
        summary.add_row("File tersimpan di", f"[cyan]{full_path}[/cyan]")
        summary.add_row("Total chapter", f"[green]{len(parts)}[/green]")
        console.print(Panel(summary, title="🎉 Berhasil!", border_style="green", box=box.ROUNDED))
        console.print()


if __name__ == "__main__":
    main()
