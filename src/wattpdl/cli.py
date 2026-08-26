"""
Modul tampilan CLI: tema warna, panel, tabel, progress bar, dan interaksi
dengan user (pilih mode, pilih chapter, dll). Tidak ada logika jaringan
langsung di sini — semua fetch data lewat modul `api`.
"""
import os
import pathlib
import time

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.prompt import Confirm, Prompt
from rich.rule import Rule
from rich.theme import Theme

from . import api

THEME = Theme({
    "primary":   "bold cyan",
    "accent":    "cyan",
    "success":   "bold green",
    "warning":   "bold yellow",
    "danger":    "bold red",
    "muted":     "dim",
    "value":     "bold white",
})

console = Console(theme=THEME)

LOGO = r"""
[primary]██╗    ██╗ █████╗ ████████╗████████╗██████╗ ██████╗ ██╗     [/primary]
[primary]██║    ██║██╔══██╗╚══██╔══╝╚══██╔══╝██╔══██╗██╔══██╗██║     [/primary]
[primary]██║ █╗ ██║███████║   ██║      ██║   ██████╔╝██║  ██║██║     [/primary]
[primary]██║███╗██║██╔══██║   ██║      ██║   ██╔═══╝ ██║  ██║██║     [/primary]
[primary]╚███╔███╔╝██║  ██║   ██║      ██║   ██║     ██████╔╝███████╗[/primary]
[muted] ╚══╝╚══╝ ╚═╝  ╚═╝   ╚═╝      ╚═╝   ╚═╝     ╚═════╝ ╚══════╝[/muted]
"""

_step_counter = {"n": 0}
_CIRCLED = ["①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩"]


def reset_steps() -> None:
    """Reset nomor tahap ke awal. Dipanggil tiap sesi (interaktif/non-interaktif) baru dimulai,
    supaya penomoran tidak terus menumpuk kalau app dipakai berkali-kali dalam satu proses Python
    (misalnya saat test, atau dipanggil berulang lewat import)."""
    _step_counter["n"] = 0


def step_rule(title: str) -> None:
    """Tampilkan pembatas antar tahap dengan nomor otomatis."""
    idx = _step_counter["n"]
    num = _CIRCLED[idx] if idx < len(_CIRCLED) else str(idx + 1)
    _step_counter["n"] += 1
    console.print()
    console.print(Rule(f"[primary]{num}  {title}[/primary]", style="accent", align="left"))


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


def confirm_overwrite(path: pathlib.Path) -> bool:
    """Tanya user apakah file yang sudah ada di folder tujuan boleh ditimpa.
    Kembalikan True kalau boleh lanjut (timpa), False kalau mau di-skip."""
    console.print(f"\n[warning]⚠  File sudah ada:[/warning] [accent]{path}[/accent]")
    return Confirm.ask("[value]Timpa file ini?[/value]", default=False)


def format_duration(seconds: float) -> str:
    """Ubah detik jadi format menit:detik yang enak dibaca."""
    seconds = int(seconds)
    minutes, secs = divmod(seconds, 60)
    if minutes:
        return f"{minutes}m {secs}d"
    return f"{secs}d"


def show_chapter_list(parts: list) -> None:
    """Tampilkan tabel nomor + judul semua chapter."""
    from rich import box
    from rich.table import Table

    table = Table(box=box.SIMPLE_HEAD, padding=(0, 1), expand=False)
    table.add_column("No", style="muted", justify="right", width=5)
    table.add_column("Judul Chapter", style="value")
    for i, part in enumerate(parts, start=1):
        table.add_row(str(i), part.get("title", f"Chapter {i}"))
    console.print(table)


def parse_chapter_selection(raw: str, total: int) -> list:
    """Terima input seperti '1,3,5-8' dan kembalikan list nomor chapter unik & urut."""
    raw = raw.replace(" ", "")
    if not raw:
        raise ValueError("Input tidak boleh kosong.")

    selected = set()
    for chunk in raw.split(","):
        if not chunk:
            continue
        if "-" in chunk:
            start_s, _, end_s = chunk.partition("-")
            if not start_s.isdigit() or not end_s.isdigit():
                raise ValueError(f"Format rentang tidak valid: '{chunk}'")
            start, end = int(start_s), int(end_s)
            if start > end:
                start, end = end, start
            selected.update(n for n in range(start, end + 1) if 1 <= n <= total)
        else:
            if not chunk.isdigit():
                raise ValueError(f"'{chunk}' bukan angka yang valid.")
            n = int(chunk)
            if 1 <= n <= total:
                selected.add(n)

    if not selected:
        raise ValueError(f"Tidak ada nomor chapter valid (rentang 1-{total}).")
    return sorted(selected)


def select_multiple_chapters(parts: list) -> list:
    """Tampilkan daftar chapter, minta user memilih beberapa. Kembalikan list (nomor, part)."""
    step_rule("Pilih Chapter")
    show_chapter_list(parts)
    while True:
        raw = Prompt.ask(
            "\n[value]Masukkan nomor chapter[/value] [muted](contoh: 1,3,5-8)[/muted]"
        )
        try:
            numbers = parse_chapter_selection(raw, len(parts))
            break
        except ValueError as e:
            console.print(f"[danger]❌  {e}[/danger]")

    console.print(f"[success]✔ {len(numbers)} chapter dipilih.[/success]")
    return [(n, parts[n - 1]) for n in numbers]


def select_single_chapter(parts: list) -> tuple:
    """Tampilkan daftar chapter, minta user memilih satu. Kembalikan (nomor, part)."""
    step_rule("Pilih Chapter")
    show_chapter_list(parts)
    while True:
        raw = Prompt.ask("\n[value]Masukkan nomor chapter[/value]").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(parts):
            n = int(raw)
            break
        console.print(f"[danger]❌  Masukkan angka antara 1-{len(parts)}.[/danger]")

    part = parts[n - 1]
    console.print(f"[success]✔ Dipilih:[/success] Chapter {n} — {part.get('title', '')}")
    return n, part


def download_chapters(indexed_parts: list, story_id: str = None) -> tuple:
    """
    Unduh sekumpulan chapter dengan progress bar.
    indexed_parts: list of (nomor_chapter, part_dict)
    story_id: kalau diisi, chapter yang sudah berhasil diunduh sebelumnya
        (tersimpan dari sesi yang macet/terhenti) akan dipakai ulang dari
        cache tanpa fetch ulang ke server — lihat modul `progress`.
    Return: (results, failed_chapters)
      results = list of (nomor_chapter, judul_chapter, teks)
    """
    from . import progress as progress_mod
    from .writers import html_to_text

    results = []
    failed = []
    cached = progress_mod.load_progress(story_id) if story_id else {}
    resumed_count = 0

    def on_retry(attempt, retries, wait, error):
        console.print(
            f"    [warning]⚠  Gagal (percobaan {attempt}/{retries}), "
            f"coba lagi dalam {wait}s… ({error})[/warning]"
        )

    progress_columns = [
        SpinnerColumn(style="accent", spinner_name="dots"),
        TextColumn("[value]{task.description}[/value]"),
        BarColumn(bar_width=32, complete_style="cyan", finished_style="success", style="grey23"),
        TextColumn("[progress.percentage]{task.percentage:>5.1f}%"),
        TextColumn("[muted]{task.completed}/{task.total}[/muted]"),
        TextColumn("[muted]•[/muted]"),
        TimeElapsedColumn(),
        TextColumn("[muted]sisa[/muted]"),
        TimeRemainingColumn(),
    ]

    with Progress(*progress_columns, console=console) as progress:
        task = progress.add_task("Menyiapkan…", total=len(indexed_parts))

        for idx, part in indexed_parts:
            part_id = part["id"]
            chapter_title = part.get("title", f"Chapter {idx}")
            cache_key = str(part_id)

            short_title = (chapter_title[:26] + "…") if len(chapter_title) > 26 else chapter_title
            progress.update(task, description=f"{short_title:<28}")

            if cache_key in cached:
                text = cached[cache_key]["text"]
                resumed_count += 1
                results.append((idx, chapter_title, text))
                progress.advance(task)
                continue

            try:
                raw_html = api.get_chapter_html(part_id, on_retry=on_retry)
                text = html_to_text(raw_html)
                if story_id:
                    progress_mod.save_chapter_progress(story_id, part_id, chapter_title, text)
            except Exception as e:
                console.print(f"\n    [danger]⚠  Chapter [{idx}] gagal:[/danger] {e}")
                text = "[GAGAL DIUNDUH — coba jalankan ulang]"
                failed.append(f"Chapter {idx}: {chapter_title}")

            results.append((idx, chapter_title, text))
            progress.advance(task)
            time.sleep(api.DELAY_SECONDS)

    if resumed_count:
        console.print(
            f"[muted]↻ {resumed_count} chapter dipakai dari progress sebelumnya (tidak diunduh ulang).[/muted]"
        )

    return results, failed
