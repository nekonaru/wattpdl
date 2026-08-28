"""
Modul tampilan CLI: tema warna, panel, tabel, progress bar, dan interaksi
dengan user (pilih mode, pilih chapter, dll). Tidak ada logika jaringan
langsung di sini — semua fetch data lewat modul `api`.
"""
import os
import pathlib

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.prompt import (  # noqa: F401 — IntPrompt dipakai via cli.IntPrompt di app.py
    Confirm,
    IntPrompt,
    Prompt,
)
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
            # Pangkas dulu ke rentang valid [1, total] SEBELUM bikin range().
            # Kalau tidak, range(start, end+1) akan mengiterasi tiap angka dari
            # start ke end walau nantinya difilter — untuk angka besar (mis. salah
            # ketik kelebihan nol, atau lewat --chapters di script otomatisasi)
            # ini bisa bikin CLI hang lama padahal ceritanya cuma beberapa chapter.
            lo, hi = max(start, 1), min(end, total)
            if lo <= hi:
                selected.update(range(lo, hi + 1))
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


def download_chapters(
    indexed_parts: list,
    story_id: str = None,
    max_workers: int = 1,
    rate_limiter=None,
    include_images: bool = False,
) -> tuple:
    """
    Unduh sekumpulan chapter dengan progress bar.
    indexed_parts: list of (nomor_chapter, part_dict)
    story_id: kalau diisi, chapter yang sudah berhasil diunduh sebelumnya
        (tersimpan dari sesi yang macet/terhenti) akan dipakai ulang dari
        cache tanpa fetch ulang ke server — lihat modul `progress`.
    max_workers: jumlah chapter yang diunduh bersamaan (paralel). 1 = berurutan
        (default, paling aman/paling lambat). >1 mempercepat unduhan cerita
        panjang, tapi tetap dijaga oleh `rate_limiter` supaya tidak membanjiri
        server Wattpad.
    rate_limiter: instance `api.AdaptiveRateLimiter` opsional, dibagi antar
        semua chapter (dan semua worker) supaya jeda otomatis melambat kalau
        server mulai balikin rate-limit. Dibuat baru kalau tidak diisi.
    include_images: kalau True, ekstrak & unduh juga gambar inline (<img>) di
        setiap chapter. Catatan: gambar inline TIDAK ikut disimpan di progress
        resume (cuma teksnya) — kalau proses diresume, gambar chapter yang
        sempat gagal di tengah jalan akan diunduh ulang, bukan dari cache.

    Return: (results, failed_chapters, images_by_idx)
      results = list of (nomor_chapter, judul_chapter, teks)
      images_by_idx = {nomor_chapter: [bytes_gambar, ...]} — kosong kalau
        include_images=False.
    """
    import threading
    from concurrent.futures import ThreadPoolExecutor, as_completed

    from . import progress as progress_mod
    from .writers import html_to_text

    if rate_limiter is None:
        rate_limiter = api.AdaptiveRateLimiter()

    results = []
    failed = []
    images_by_idx = {}
    store = progress_mod.ProgressStore(story_id) if story_id else None
    resumed_count = 0
    print_lock = threading.Lock()

    def on_retry(attempt, retries, wait, error):
        with print_lock:
            console.print(
                f"    [warning]⚠  Gagal (percobaan {attempt}/{retries}), "
                f"coba lagi dalam {wait}s… ({error})[/warning]"
            )

    def fetch_one(idx, part):
        """Kerjakan 1 chapter: pakai cache kalau ada, atau unduh + retry.
        Aman dipanggil dari banyak thread sekaligus (tidak ada shared mutable
        state kecuali lewat `store`/`rate_limiter`, yang sudah thread-safe).

        Jeda `rate_limiter.wait()` sengaja dipanggil DI SINI (bukan di
        caller/loop luar) supaya konsisten berlaku baik di jalur sequential
        maupun paralel — sebelumnya jeda cuma diterapkan di jalur sequential,
        jadi mode `--workers > 1` menembak API tanpa throttle adaptif sama
        sekali. Gambar inline juga ikut kena jeda yang sama per item, karena
        sebelumnya unduhan gambar tidak pernah melalui rate limiter sama sekali
        di kedua jalur."""
        part_id = part["id"]
        chapter_title = part.get("title", f"Chapter {idx}")

        if store is not None and store.has(part_id):
            cached = store.get(part_id)
            return idx, chapter_title, cached["text"], [], True, None

        try:
            raw_html = api.get_chapter_html(part_id, on_retry=on_retry, rate_limiter=rate_limiter)
            text = html_to_text(raw_html)
            rate_limiter.wait()
            images = []
            if include_images:
                for img_url in api.extract_chapter_images(raw_html):
                    img_bytes = api.download_image(img_url)
                    if img_bytes:
                        images.append(img_bytes)
                    rate_limiter.wait()
            if store is not None:
                store.mark_done(part_id, chapter_title, text)
            return idx, chapter_title, text, images, False, None
        except Exception as e:
            # Chapter gagal total (retry di get_chapter_html sudah habis). Tetap
            # panggil wait() di sini juga — tanpa ini, begitu 1 chapter gagal,
            # eksekusi lompat ke chapter berikutnya TANPA jeda sama sekali,
            # padahal rate_limiter._level sudah naik gara-gara kegagalan ini
            # (dilaporkan lewat report_throttled() di get_chapter_html kalau
            # sebabnya 429/503). Request beruntun tanpa jeda pasca-kegagalan
            # justru bisa memperparah rate-limiting di server.
            rate_limiter.wait()
            return idx, chapter_title, "[GAGAL DIUNDUH — coba jalankan ulang]", [], False, e

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

        if max_workers <= 1:
            # Jalur sederhana berurutan (default) — dipertahankan terpisah dari
            # jalur paralel di bawah supaya perilakunya persis sama seperti
            # sebelumnya (termasuk urutan pesan di layar), bukan cuma kasus
            # khusus dari ThreadPoolExecutor(max_workers=1).
            for idx, part in indexed_parts:
                chapter_title = part.get("title", f"Chapter {idx}")
                short_title = (chapter_title[:26] + "…") if len(chapter_title) > 26 else chapter_title
                progress.update(task, description=f"{short_title:<28}")

                _, _, text, images, was_cached, err = fetch_one(idx, part)
                if was_cached:
                    resumed_count += 1
                elif err is not None:
                    console.print(f"\n    [danger]⚠  Chapter [{idx}] gagal:[/danger] {err}")
                    failed.append((idx, f"Chapter {idx}: {chapter_title}"))

                results.append((idx, chapter_title, text))
                if images:
                    images_by_idx[idx] = images
                progress.advance(task)
        else:
            # Jalur paralel — beberapa chapter diunduh bersamaan lewat thread
            # pool. Urutan penyelesaian tidak dijamin sama dengan urutan
            # chapter, jadi `results` disortir ulang berdasarkan idx di akhir.
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(fetch_one, idx, part): (idx, part) for idx, part in indexed_parts}
                for future in as_completed(futures):
                    idx, part = futures[future]
                    chapter_title = part.get("title", f"Chapter {idx}")
                    _, _, text, images, was_cached, err = future.result()
                    if was_cached:
                        resumed_count += 1
                    elif err is not None:
                        with print_lock:
                            console.print(f"\n    [danger]⚠  Chapter [{idx}] gagal:[/danger] {err}")
                        failed.append((idx, f"Chapter {idx}: {chapter_title}"))

                    results.append((idx, chapter_title, text))
                    if images:
                        images_by_idx[idx] = images
                    progress.update(task, description=f"{len(results)}/{len(indexed_parts)} chapter")
                    progress.advance(task)
            results.sort(key=lambda r: r[0])

    if resumed_count:
        console.print(
            f"[muted]↻ {resumed_count} chapter dipakai dari progress sebelumnya (tidak diunduh ulang).[/muted]"
        )

    # `failed` dikumpulkan sbg (idx, label) supaya bisa disortir NUMERIK
    # berdasarkan nomor chapter — bukan alfabetis. Sort string biasa bikin
    # "Chapter 10" muncul sebelum "Chapter 2" di ringkasan mode paralel
    # (urutan penyelesaian ThreadPoolExecutor tidak berurutan).
    failed = [label for _, label in sorted(failed, key=lambda item: item[0])]

    return results, failed, images_by_idx
