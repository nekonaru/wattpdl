"""
CLI display module: color theme, panels, tables, progress bar, and interaction
with the user (choose mode, choose chapters, etc.). No direct network logic
here; all data fetching goes through the `api` module.
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
from rich.prompt import (  # noqa: F401 - IntPrompt is used via cli.IntPrompt in app.py
    Confirm,
    IntPrompt,
    Prompt,
)
from rich.rule import Rule
from rich.theme import Theme

from . import api
from .i18n import t

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
    """Reset the step number to the start. Called whenever a new (interactive/non-interactive)
    session begins, so the numbering does not keep accumulating if the app is used many times in one Python process
    (for example during tests, or called repeatedly via import)."""
    _step_counter["n"] = 0


def step_rule(title: str) -> None:
    """Show a divider between steps with an automatic number."""
    idx = _step_counter["n"]
    num = _CIRCLED[idx] if idx < len(_CIRCLED) else str(idx + 1)
    _step_counter["n"] += 1
    console.print()
    console.print(Rule(f"[primary]{num}  {title}[/primary]", style="accent", align="left"))


def get_default_download_dir() -> pathlib.Path:
    """
    Return the operating system's default Downloads folder:
      - Windows : C:\\Users\\<user>\\Downloads
      - macOS   : /Users/<user>/Downloads
      - Linux   : /home/<user>/Downloads  (or XDG_DOWNLOAD_DIR)
    """
    xdg = os.environ.get("XDG_DOWNLOAD_DIR", "").strip()
    if xdg and pathlib.Path(xdg).is_dir():
        return pathlib.Path(xdg)

    downloads = pathlib.Path.home() / "Downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    return downloads


def confirm_overwrite(path: pathlib.Path) -> bool:
    """Ask the user whether the file that already exists in the target folder may be overwritten.
    Return True to continue (overwrite), False to skip."""
    console.print(f"\n[warning]{t('warn.file_exists')}[/warning] [accent]{path}[/accent]")
    return Confirm.ask(f"[value]{t('prompt.overwrite')}[/value]", default=False)


def format_duration(seconds: float) -> str:
    """Turn seconds into a readable minutes:seconds format."""
    seconds = int(seconds)
    minutes, secs = divmod(seconds, 60)
    unit = t("unit.seconds")
    if minutes:
        return f"{minutes}m {secs}{unit}"
    return f"{secs}{unit}"


def show_chapter_list(parts: list) -> None:
    """Show a table of the number + title of every chapter."""
    from rich import box
    from rich.table import Table

    table = Table(box=box.SIMPLE_HEAD, padding=(0, 1), expand=False)
    table.add_column(t("table.no"), style="muted", justify="right", width=5)
    table.add_column(t("table.chapter_title"), style="value")
    for i, part in enumerate(parts, start=1):
        table.add_row(str(i), part.get("title", f"Chapter {i}"))
    console.print(table)


def parse_chapter_selection(raw: str, total: int) -> list:
    """Accept input like '1,3,5-8' and return a list of unique, sorted chapter numbers."""
    raw = raw.replace(" ", "")
    if not raw:
        raise ValueError(t("err.empty_input"))

    selected = set()
    for chunk in raw.split(","):
        if not chunk:
            continue
        if "-" in chunk:
            start_s, _, end_s = chunk.partition("-")
            if not start_s.isdigit() or not end_s.isdigit():
                raise ValueError(t("err.bad_range", chunk=chunk))
            start, end = int(start_s), int(end_s)
            if start > end:
                start, end = end, start
            # Clamp to the valid range [1, total] BEFORE building range().
            # Otherwise, range(start, end+1) would iterate over every number from
            # start to end even though it is filtered afterwards, and for large numbers (e.g. a typo
            # with too many zeros, or via --chapters in an automation script)
            # this can make the CLI hang for a long time even though the story only has a few chapters.
            lo, hi = max(start, 1), min(end, total)
            if lo <= hi:
                selected.update(range(lo, hi + 1))
        else:
            if not chunk.isdigit():
                raise ValueError(t("err.not_number", chunk=chunk))
            n = int(chunk)
            if 1 <= n <= total:
                selected.add(n)

    if not selected:
        raise ValueError(t("err.no_valid_chapter", total=total))
    return sorted(selected)


def select_multiple_chapters(parts: list) -> list:
    """Show the chapter list and ask the user to pick several. Return a list of (number, part)."""
    step_rule(t("step.pick_chapter"))
    show_chapter_list(parts)
    while True:
        raw = Prompt.ask(
            f"\n[value]{t('prompt.chapter_numbers')}[/value] [muted]{t('prompt.chapter_numbers_hint')}[/muted]"
        )
        try:
            numbers = parse_chapter_selection(raw, len(parts))
            break
        except ValueError as e:
            console.print(f"[danger]❌  {e}[/danger]")

    console.print(f"[success]{t('ok.chapters_selected', n=len(numbers))}[/success]")
    return [(n, parts[n - 1]) for n in numbers]


def select_single_chapter(parts: list) -> tuple:
    """Show the chapter list and ask the user to pick one. Return (number, part)."""
    step_rule(t("step.pick_chapter"))
    show_chapter_list(parts)
    while True:
        raw = Prompt.ask(f"\n[value]{t('prompt.chapter_numbers')}[/value]").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(parts):
            n = int(raw)
            break
        console.print(f"[danger]{t('err.number_between', total=len(parts))}[/danger]")

    part = parts[n - 1]
    console.print(f"[success]{t('ok.selected')}[/success] Chapter {n}: {part.get('title', '')}")
    return n, part


def download_chapters(
    indexed_parts: list,
    story_id: str = None,
    max_workers: int = 1,
    rate_limiter=None,
    include_images: bool = False,
) -> tuple:
    """
    Download a set of chapters with a progress bar.
    indexed_parts: list of (chapter_number, part_dict)
    story_id: if given, chapters that were already downloaded successfully before
        (saved from a session that hung/stopped) are reused from the
        cache without fetching from the server again, see the `progress` module.
    max_workers: number of chapters downloaded at the same time (parallel). 1 = sequential
        (default, safest/slowest). >1 speeds up long story downloads,
        but is still guarded by `rate_limiter` so Wattpad's server is not
        flooded.
    rate_limiter: optional `api.AdaptiveRateLimiter` instance, shared across
        all chapters (and all workers) so the delay slows down automatically when the
        server starts returning rate limits. Created fresh if not given.
    include_images: if True, also extract & download inline images (<img>) in
        every chapter. Note: inline images are NOT saved in the resume
        progress (only the text), so if the process is resumed, images for chapters that
        failed midway are downloaded again, not taken from the cache.

    Return: (results, failed_chapters, images_by_idx)
      results = list of (chapter_number, chapter_title, text)
      images_by_idx = {chapter_number: [image_bytes, ...]}, empty if
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
                f"[warning]{t('retry.failed', attempt=attempt, retries=retries, wait=wait, error=error)}[/warning]"
            )

    def fetch_one(idx, part):
        """Handle 1 chapter: use the cache if present, or download + retry.
        Safe to call from many threads at once (no shared mutable
        state except through `store`/`rate_limiter`, which are already thread-safe).

        The `rate_limiter.wait()` delay is deliberately called HERE (not in the
        caller/outer loop) so it applies consistently on both the sequential
        and the parallel path. Previously the delay was only applied on the sequential path,
        so `--workers > 1` mode hit the API without any adaptive throttle at
        all. Inline images are also subject to the same per-item delay, because
        image downloads previously never went through the rate limiter at all
        on either path."""
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
            # The chapter failed completely (the retries in get_chapter_html are used up). Still
            # call wait() here too: without it, as soon as 1 chapter fails,
            # execution jumps to the next chapter with NO delay at all,
            # even though rate_limiter._level has already gone up because of this failure
            # (reported via report_throttled() in get_chapter_html when
            # the cause is 429/503). Back-to-back requests with no delay after a failure
            # can actually make the server's rate limiting worse.
            rate_limiter.wait()
            return idx, chapter_title, t("chapter.failed_placeholder"), [], False, e

    progress_columns = [
        SpinnerColumn(style="accent", spinner_name="dots"),
        TextColumn("[value]{task.description}[/value]"),
        BarColumn(bar_width=32, complete_style="cyan", finished_style="success", style="grey23"),
        TextColumn("[progress.percentage]{task.percentage:>5.1f}%"),
        TextColumn("[muted]{task.completed}/{task.total}[/muted]"),
        TextColumn("[muted]•[/muted]"),
        TimeElapsedColumn(),
        TextColumn(f"[muted]{t('progress.remaining')}[/muted]"),
        TimeRemainingColumn(),
    ]

    with Progress(*progress_columns, console=console) as progress:
        task = progress.add_task(t("progress.preparing"), total=len(indexed_parts))

        if max_workers <= 1:
            # Simple sequential path (default), kept separate from
            # the parallel path below so its behavior is exactly the same as
            # before (including the order of messages on screen), not just a special
            # case of ThreadPoolExecutor(max_workers=1).
            for idx, part in indexed_parts:
                chapter_title = part.get("title", f"Chapter {idx}")
                short_title = (chapter_title[:26] + "…") if len(chapter_title) > 26 else chapter_title
                progress.update(task, description=f"{short_title:<28}")

                _, _, text, images, was_cached, err = fetch_one(idx, part)
                if was_cached:
                    resumed_count += 1
                elif err is not None:
                    console.print(f"[danger]{t('err.chapter_failed', idx=idx)}[/danger] {err}")
                    failed.append((idx, f"Chapter {idx}: {chapter_title}"))

                results.append((idx, chapter_title, text))
                if images:
                    images_by_idx[idx] = images
                progress.advance(task)
        else:
            # Parallel path, several chapters are downloaded at the same time through a thread
            # pool. The completion order is not guaranteed to match the
            # chapter order, so `results` is sorted again by idx at the end.
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
                            console.print(f"[danger]{t('err.chapter_failed', idx=idx)}[/danger] {err}")
                        failed.append((idx, f"Chapter {idx}: {chapter_title}"))

                    results.append((idx, chapter_title, text))
                    if images:
                        images_by_idx[idx] = images
                    progress.update(task, description=t("progress.chapter_count", done=len(results), total=len(indexed_parts)))
                    progress.advance(task)
            results.sort(key=lambda r: r[0])

    if resumed_count:
        console.print(
            f"[muted]{t('info.resumed', n=resumed_count)}[/muted]"
        )

    # `failed` is collected as (idx, label) so it can be sorted NUMERICALLY
    # by chapter number, not alphabetically. A plain string sort would put
    # "Chapter 10" before "Chapter 2" in the summary of parallel mode
    # (the completion order of ThreadPoolExecutor is not sequential).
    failed = [label for _, label in sorted(failed, key=lambda item: item[0])]

    return results, failed, images_by_idx
