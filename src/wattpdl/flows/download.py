"""The shared single-story download flow."""
import sys
import time

from rich import box
from rich.panel import Panel
from rich.table import Table

from .. import api, cli, library
from .. import config as config_mod
from .. import progress as progress_mod
from ..cli import console, step_rule
from ..i18n import t
from .common import (
    REPORT_ENTRIES,
    _output_base_name,
    _output_path,
    _write_output,
    resolve_chapters,
    should_skip_existing,
)


def run_download(story_id, title, author, parts, mode, file_format, save_dir,
                  chapters_arg=None, chapter_arg=None, meta=None, cover_bytes=None,
                  skip_existing=False, interactive=False, workers=1, include_images=False,
                  language="id", retries=None, timeout=None, dry_run=False,
                  keep_progress_on_success=False, filename=None, formats=None,
                  no_library=False, pdf_pagesize=None, pdf_font_size=None,
                  save_preferences=True):
    """Shared download flow for both interactive and non-interactive modes."""
    indexed_parts = resolve_chapters(mode, parts, chapters_arg, chapter_arg)
    codes = list(formats) if formats else [file_format]
    base_name = _output_base_name(title, filename)
    targets = [(code, _output_path(save_dir, base_name, mode, code, indexed_parts)) for code in codes]

    for _code, path in targets:
        try:
            path.exists()
        except OSError as e:
            # The file name can still exceed the OS limit even after safe_filename().
            console.print(f"[danger]{t('err.path_invalid')}[/danger] {e}")
            console.print(f"[muted]{t('info.path_tried', path=path)}[/muted]")
            console.print(f"[muted]{t('hint.shorter_path')}[/muted]")
            sys.exit(1)

    if dry_run:
        reused, to_download = 0, 0
        if story_id:
            store = progress_mod.ProgressStore(story_id)
            for _, part in indexed_parts:
                if store.has(part["id"]):
                    reused += 1
                else:
                    to_download += 1
        else:
            to_download = len(indexed_parts)
        console.print(f"[warning]{t('dryrun.title')}[/warning]")
        for code, path in targets:
            ext = {"2": "docx", "3": "epub", "4": "md", "5": "pdf"}.get(code, "txt")
            console.print(f"[muted]{t('dryrun.path')}[/muted] [accent]{path}[/accent]")
            console.print(f"[muted]{t('dryrun.exists')}[/muted] [accent]{str(path.exists()).lower()}[/accent]")
            console.print(f"[muted]{t('dryrun.mode')}[/muted] [accent]{mode} ({ext})[/accent]")
        console.print(f"[muted]{t('dryrun.chapters')}[/muted] [accent]{len(indexed_parts)}[/accent]")
        console.print(f"[muted]{t('dryrun.reused')}[/muted] [accent]{reused}[/accent]")
        console.print(f"[muted]{t('dryrun.to_download')}[/muted] [accent]{to_download}[/accent]")
        return

    write_targets = []
    for code, path in targets:
        if path.exists():
            if interactive:
                if not cli.confirm_overwrite(path):
                    console.print(f"[muted]{t('info.skipped_existing_kept')}[/muted]")
                    continue
            elif should_skip_existing(path, skip_existing):
                console.print(
                    f"[muted]{t('info.skipped_existing')}[/muted] [accent]{path}[/accent]\n"
                    f"[muted]{t('hint.remove_skip_existing')}[/muted]"
                )
                continue
        write_targets.append((code, path))
    if not write_targets:
        return

    for _code, path in write_targets:
        console.print(f"[value]{t('info.saved_at')}[/value] [accent]{path}[/accent]")

    step_rule(t("step.downloading"))
    start_time = time.time()
    rate_limiter = api.AdaptiveRateLimiter()
    results, failed_chapters, images_by_idx = cli.download_chapters(
        indexed_parts, story_id=story_id, max_workers=workers,
        rate_limiter=rate_limiter, include_images=include_images,
        retries=retries, timeout=timeout,
    )
    elapsed = cli.format_duration(time.time() - start_time)
    if include_images:
        n_images = sum(len(v) for v in images_by_idx.values())
        if n_images:
            console.print(f"[muted]{t('info.images_downloaded', n=n_images)}[/muted]")
        else:
            console.print(f"[warning]{t('warn.no_images')}[/warning]")

    written_paths = []
    try:
        for code, path in write_targets:
            _write_output(path, title, author, story_id, results, mode, code,
                          meta, cover_bytes, images_by_idx, language,
                          pdf_pagesize=pdf_pagesize, pdf_font_size=pdf_font_size)
            written_paths.append(path)
    except OSError as e:
        # The chapters were already downloaded, so a write failure at the last
        # second must not look like a raw traceback; progress is preserved.
        console.print(f"[danger]{t('err.write_failed')}[/danger] {e}")
        console.print(f"[muted]{t('info.path_tried', path=path)}[/muted]")
        console.print(f"[muted]{t('hint.progress_kept')}[/muted]")
        sys.exit(1)

    REPORT_ENTRIES.append({
        "story_id": str(story_id), "title": title, "mode": mode,
        "formats": [{"1": "txt", "2": "docx", "3": "epub", "4": "md", "5": "pdf"}.get(c, c) for c, _ in write_targets],
        "chapters": len(indexed_parts), "succeeded": len(results) - len(failed_chapters),
        "failed": len(failed_chapters), "elapsed": elapsed,
        "files": [str(p) for p in written_paths], "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    })

    step_rule(t("step.summary"))
    summary = Table(show_header=False, box=box.SIMPLE, padding=(0, 1), expand=False)
    summary.add_column(style="muted")
    summary.add_column(style="value")
    for path in written_paths:
        summary.add_row(t("sum.file_saved"), f"[accent]{path}[/accent]")
    summary.add_row(t("sum.success"), f"[success]{len(results) - len(failed_chapters)}/{len(results)}[/success]")
    if failed_chapters:
        summary.add_row(t("sum.failed"), f"[danger]{len(failed_chapters)}[/danger]")
    summary.add_row(t("sum.total_time"), elapsed)

    if failed_chapters:
        fail_list = "\n".join(f"[danger]• {ch}[/danger]" for ch in failed_chapters)
        body = Table.grid(padding=(0, 0))
        body.add_row(summary)
        body.add_row("")
        body.add_row(f"[muted]{t('sum.failed_chapters')}[/muted]\n{fail_list}")
        console.print(Panel(
            body,
            title=f"[warning]{t('sum.title_partial')}[/warning]",
            border_style="warning",
            box=box.ROUNDED,
            padding=(1, 2),
        ))
        console.print(f"[muted]{t('sum.partial_hint')}[/muted]\n")
    else:
        # All chapters succeeded -> this story's resume progress file is no longer needed,
        # unless the caller wants to keep it (used by --update-library so the next update
        # only fetches the chapters that were added since).
        if not keep_progress_on_success:
            progress_mod.clear_progress(story_id)
        if mode in ("1", "2") and not no_library:
            # Record it in the library so --check-updates / --watch can detect
            # when this story gets new chapters later.
            library.remember_story(story_id, title, len(parts))
        if not no_library:
            formats_for_history = [
                {"1": "txt", "2": "docx", "3": "epub", "4": "md", "5": "pdf"}.get(c, c)
                for c, _ in write_targets
            ]
            library.record_download(story_id, title, formats_for_history, len(indexed_parts))
        console.print(Panel(
            summary,
            title=f"[success]{t('sum.title_done')}[/success]",
            border_style="success",
            box=box.DOUBLE,
            padding=(1, 2),
        ))
        console.print()

    # Save preferences once per run; batch flows do it at the end themselves.
    if save_preferences:
        config_mod.save_config(save_dir=str(save_dir), file_format=file_format)
