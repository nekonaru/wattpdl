# Changelog

All notable changes to this project are documented in this file. The format follows the release notes; see [CHANGELOG.id.md](CHANGELOG.id.md) for the Bahasa Indonesia version.

## v1.12.0

Search filters, JSON discovery, download history, PDF/EPUB options, and a fix for the broken author endpoint.

### New features

- **Search filters.** `--search-status completed|ongoing`, `--search-min-chapters N`, `--search-sort votes|chapters|title` and `--search-language NAME` filter and sort results client-side (Wattpad's search API ignores those parameters). `--search --json` prints the results as JSON.
- **Author info.** `--author-info USER` lists an author's stories with chapter totals, without downloading. `--author-info --json` prints JSON.
- **Download history.** Successful downloads are recorded in `~/.wattpdl/history.json`; `--history` and `--history --json` show them. `--no-library` skips both library and history recording.
- **PDF layout.** `--pdf-pagesize A4|A5` and `--pdf-font-size N` (6-24) control the generated PDFs.
- **EPUB metadata.** The source story URL and Completed/Ongoing status are now written as Dublin Core metadata.
- **Watch for scripts.** `--watch-notify-json` prints one JSON line per new chapter; `--watch-max-iterations N` is now documented and exposed.

### Bug fixes

- **Author downloads work again.** The Wattpad endpoint used by `--user` was `/users/{username}/stories/published`, which returns 404 for every real author. It is now `/users/{username}/stories`, verified live; `--user` and `--author-info` both use it.
- **`--author-info` no longer crashes on a 404** from a deleted or private author; it shows a clear message instead.

## v1.11.0

Multi-format output, download reports, CLI tooling, and an audit round that raised test coverage.

### New features

- **Several formats from one download.** `--format txt,epub` or `--format all` writes every requested output from the same downloaded chapters. In mode 2 each format gets its own zip.
- **Download report.** `--report PATH.json` or `.csv` records story ID, title, mode, formats, chapter counts, timing, and output paths for every download in the run.
- **Preference commands.** `--config` shows saved preferences; `--config-set file_format=epub` changes one.
- **Doctor.** `--doctor` checks dependency imports, data folders, preferences, and Wattpad API connectivity in one command.
- **Shell completion.** `--completion bash|zsh|fish|powershell` prints a completion script for wattpdl flags.
- **Quiet / verbose.** `--quiet` suppresses normal output for cron; `--verbose` prints the active options.

### Improvements

- **Atomic output files.** Writers now write to a temporary file in the target folder and rename it into place, so a crash or write error never leaves a half-written result.
- **Test coverage raised** from 69% to 82% (307 tests), with an 80% floor enforced in CI.

## v1.10.0

Batch downloads from a file and custom file names, plus an audit round.

### New features

- **Batch from file.** `--file PATH` downloads every story listed in a file, one ID or link per line (`#` for comments), in mode 1 or 2. A failing story is skipped and reported at the end instead of aborting the rest.
- **Custom file name.** `--filename "My Series - Book 1"` overrides the output base name for single-story downloads (`--id`).

### Bug fixes

- **Long multibyte titles no longer overflow the file name limit.** `safe_filename` now caps by UTF-8 bytes (100 bytes, not 100 characters), so CJK and other multibyte titles cannot exceed the 255-byte limit on Linux/macOS.
- **Batch runs no longer stop on a deleted or private story.** `--user` now skips a story that cannot be fetched (with a warning) and continues with the rest, like `--update-library` already did. A failure summary is printed at the end.
- **A full or read-only disk no longer fails a chapter.** Resume progress writes are now best-effort; the chapter still counts as downloaded.
- **Saved preferences with an unknown file format fall back to `txt`** instead of passing through as-is.
- **HTTP connection pooling now fits the full worker count** (50 instead of 10), so large `--workers` values reuse connections.

## v1.9.0

Search results are paged, 10 at a time.

### New features

- **Search paging.** `--search` results are shown 10 per page; type `n` for the next page and `p` for the previous one. Indices are global across pages, so story #13 is opened with `13` no matter which page is on screen, and `--select` accepts the same global numbers in non-interactive mode.
- **`--search-limit N`** controls how many results are fetched (default 40, max 100). Popular queries no longer stop at the top 10.

## v1.8.1

### Bug fixes

- **--output-dir now applies in interactive mode.** Typing Enter at the save-folder prompt saves into the folder passed via `--output-dir`; previously the flag was silently ignored in interactive mode and the saved config default was used instead.

## v1.8.0

Search Wattpad stories and download fanfics by index.

### New features

- **Search stories.** `--search "<query>"` lists the matching stories by index (title, author, chapter count, status) using Wattpad's public search. Without `--select`, you are asked which indices to download (a range like `1-8,10`, or `all`). For scripting, pass them directly: `--search "query" --select 1-8,10 --mode 1`. Modes 1 and 2 only, like `--user`.

## v1.7.0

Library management, story info, and HTTP tuning for power users, plus a security hardening pass.

### New features

- **Library management.** `--library` lists every story recorded as fully downloaded; `--library-forget <id>` stops tracking one story.
- **`--update-library`.** Re-downloads every recorded story that has new chapters on Wattpad in one command; resume progress is kept, so only the new chapters are fetched.
- **`--check-updates` and `--library --json`.** Both commands print machine-readable JSON for scripting and automation.
- **`wattpdl --info --id <id>`.** Shows a story's details (author, chapter count, status, genre, description) without downloading.
- **`--retries N` and `--timeout N`.** Control the HTTP retry count per chapter (default 3, max 10) and the timeout of every HTTP request (default 20 seconds).
- **`--dry-run`.** Simulates a download: prints the target file, how many chapters are selected, and how many would be reused from the resume cache, without writing anything.

### Bug fixes

- **Legacy Windows consoles no longer crash.** Stdout and stderr are reconfigured to UTF-8 at startup with a lossy fallback; previously the banner and step markers raised UnicodeEncodeError on a cp1252 console.
- **Inline images cannot reach internal networks.** Downloads from non-globally-routable hosts (loopback, private ranges, link-local including the cloud metadata endpoint, CGNAT) are rejected, the scheme must be http/https, and images are capped at 25 MB.
- **Corrupt cache files no longer crash the tool.** The library, progress, config, metadata-cache and update-check loaders now require a JSON object at the top level and treat anything else as missing.
- **Stricter argument validation.** `--user` only accepts valid Wattpad usernames, `--watch-interval` must be at least 1 second, `--retries` at most 10, and `--json` is rejected outside `--library`/`--check-updates`.

### Improvements

- **CI/CD hardened.** GitHub Actions pinned to commit SHAs, token permissions reduced to `contents: read` (publish keeps only `id-token: write`), pip-audit added to CI, coverage floor 65%, Dependabot for pip and GitHub Actions, branch protection on `main` with required checks, and the test matrix runs on Python 3.9 to 3.12.

## v1.6.0

Connection pooling for faster downloads, Pillow is now a declared dependency, and an internal cleanup.

### Improvements

- **Connection pooling.** HTTP requests now reuse TCP/TLS connections per thread instead of a fresh handshake per chapter, which speeds up long downloads, especially with `--workers`.
- **Pillow is now a declared dependency.** It was already used for PDF image processing but only arrived transitively through reportlab; `pip install wattpdl` now guarantees it.
- **Clearer chapter errors.** A chapter that is deleted or restricted (404/403 when fetching its text) now shows the same clear message style as the story-level errors.
- **Internal cleanup.** Shared HTTP session, deduplicated helpers, and tidied modules. Command-line behavior is unchanged.

### Bug fixes

- **Python 3.9 installs no longer pull a broken reportlab.** reportlab 5 declares Python 3.9 support in its metadata but fails to import on 3.9; installs on Python 3.9 are now pinned to reportlab 4.x.

## v1.5.0

WattPDL now speaks English by default and ships with fully bilingual English and Indonesian documentation.

### New features

- **English and Indonesian CLI.** Menus, prompts, tables, progress, warnings, error messages, and `--help` are now fully translatable via `--ui-lang en|id`. English is the new default, and the choice is remembered.
- **More ways to set the language.** The `WATTPDL_LANG` environment variable and the `ui_lang` value in `~/.wattpdl/config.json`. Priority: `--ui-lang`, then `WATTPDL_LANG`, then config, then `en`.
- **Bilingual documentation.** `README.md` and `CONTRIBUTING.md` are now in English, with Indonesian versions in `README.id.md` and `CONTRIBUTING.id.md`.

### Breaking changes

- **The default display language is now English.** Run `wattpdl --ui-lang id` once to switch back to Indonesian; the choice is remembered afterwards.
- **Labels inside generated files are now English.** `oleh` became `by`, and `Sumber` became `Source:` in `.txt`, `.md`, `.docx`, `.epub`, and `.pdf`. Files you already downloaded are not changed.
- **Default file names changed.** Mode 3 now produces `Story_Title_selected.<ext>` (was `_pilihan`), and an empty title falls back to `wattpad_story` (was `cerita_wattpad`). If you use `--skip-existing` with mode 3, those stories will be downloaded once more under the new name.

### Improvements

- **New i18n module.** `i18n.py` is a pure, dependency-free dictionary, and all user-facing text goes through `t("key")`; a test makes sure both languages always have the same keys and placeholders.
- **Docs synced with the code.** All 5 formats (`.txt`, `.docx`, `.epub`, `.md`, `.pdf`), the full argument table, and the output structure (including `.pdf`) are now documented accurately.
- **Code comments translated to English**, and em dashes were removed from code and docs.
- **21 new tests** for language resolution, translations, and translated error messages, for a total of **154 tests**, all passing on Python 3.9 to 3.12.

## v1.4.0

Parallel downloads, adaptive rate limiting, a PDF format, inline images, author downloads, update detection, and watch mode.

### New features

- **Parallel downloads.** `--workers N` downloads several chapters at once, which speeds up long stories significantly. The default stays 1, sequential and safest.
- **Adaptive rate limit.** The delay between chapters slows down automatically when Wattpad starts limiting requests (429) or reports the server as busy (503), then speeds up again gradually. Especially useful together with `--workers`.
- **PDF format.** A fifth format, `.pdf` (via `reportlab`). Cover and inline images are supported in PDF too.
- **Inline images.** `--include-images` downloads and embeds the images inside chapter text (not just the cover) into `.docx`, `.epub`, and `.pdf`. Very tall webtoon/comic strips are sliced across PDF pages so they stay readable.
- **Download by author.** `--user <username>` lists an author's stories and downloads all of them (`--user-select all`) or a selection (`--user-select 1,3,5-8`).
- **New chapter detection.** `--check-updates` reports ongoing stories you have downloaded (tracked in `~/.wattpdl/library.json`) that already have new chapters.
- **Watch mode.** `--watch` monitors one story continuously (interval via `--watch-interval`, default 1800 seconds) and re-downloads as soon as a new chapter appears. Stop it with Ctrl+C.
- **Short metadata cache.** Story info is cached for 5 minutes, so repeated runs for the same story do not always hit the Wattpad API. Disable it with `--no-cache`.
- **Automatic update check.** Tells you at startup when a newer wattpdl version is on PyPI (at most once a day, never disturbs the main process if it fails). Disable it with `--no-update-check`.
- **Specific error messages.** Deleted or wrong-ID stories (404) are now told apart from private or restricted ones (403).
- **`--version`.** Prints the installed wattpdl version from the terminal.

### Improvements

- **Progress store.** Progress is read once per session and kept in memory instead of re-reading the whole file per chapter (previously O(n squared)); thread-safe for parallel downloads.
- **43 new tests** for all of the above (rate limiter, PDF, inline images, `--user`, `--check-updates`, `--watch`, cache, updater), for a total of **127 tests**, all passing.
- **Verified in a clean virtualenv**, not just the development environment, so no dependency is missed.

## v1.3.0

Non-interactive mode, automatic resume, and specific chapter selection.

### New features

- **Non-interactive mode.** Set `--id` and wattpdl runs without any prompt at all, ideal for cron jobs, other scripts, or CI. Without `--id`, it stays interactive as usual.
- **Automatic resume.** If a download stops midway (connection lost, terminal closed, laptop shut down), running again with the same story continues from the last succeeded chapter instead of starting over. Progress is stored per story in `~/.wattpdl/progress/`.
- **Specific chapter selection.** Two new modes: `--mode 3` picks several chapters (`--chapters 1,3,5-8`) into one combined file, and `--mode 4` downloads a single chapter (`--chapter 5`).
- **Markdown format.** A fourth format, `.md`; the available formats are now `.txt`, `.docx`, `.epub`, `.md`.
- **Saved preferences.** The save folder and output format are remembered in `~/.wattpdl/config.json`, so you don't have to fill them in every time (override anytime via `--output-dir`/`--format`).
- **`--skip-existing`.** Skips output files that already exist instead of overwriting them, handy for scheduled bulk downloads.
- **`--no-cover`.** Turns off cover embedding into `.docx`/`.epub` when you don't need it.

### Bug fixes

- **Crash on Python 3.9.** A `bytes | None` annotation (Python 3.10+ syntax) broke import on 3.9 even though the project claims 3.9+ support; changed to `Optional[bytes]`.
- **CLI freeze on wrong chapter ranges.** `--chapters 1-500000000` (or a typo with extra zeros) now truncates the range to the actual chapter count before iterating.
- **"File name too long" crash.** Mode 4 combined the story title and chapter title into one file name, which could exceed OS limits and crash at the last second; file names are now truncated to a safe length with graceful fallback handling.
- **Windows reserved device names.** Chapter titles that are a single word like `Con`, `Aux`, `Nul`, or `Com1` are prefixed automatically so they can be saved on Windows.

### Improvements

- **Regression tests for all four fixes**, for a total of **82 tests**, all passing on Python 3.9 to 3.12.

## v1.2.1

Bug fixes from a full audit, plus project structure cleanup.

### Bug fixes

- **Connection failures no longer dump raw tracebacks.** Network errors (drop/timeout) now show a clear error message.
- **Duplicate EPUB identifiers.** Zip-per-chapter mode used to produce all EPUBs with the exact same identifier (breaking the EPUB spec); each file now gets a unique identifier.
- **Silent empty chapters.** A chapter retried with `retries=0` used to be stored empty without a word; now a clear error is raised.
- **Save folder fallback failure.** The fallback to the default folder is now handled too when the default folder itself cannot be created (for example a read-only home directory).
- **Chapter links not recognized.** Wattpad per-chapter share links now get a specific message ("this is a chapter link, not a story link").

### Improvements

- **Removed 7 legacy files** in the repo root (`api.py`, `cli.py`, `writers.py`, etc.), leftovers from before the `src/wattpdl/` restructure that made CI fail to collect tests.
- **README tidied.** ASCII art banner removed.
- **8 new tests** covering the five fixes above, for a total of **62 tests**, all passing on Python 3.9 to 3.12.
- **CI matrix no longer fail-fast**, so every Python version runs to completion even if one fails.

## v1.2.0

Support for the EPUB format.

### New features

- **EPUB format.** Download stories directly as ebooks, complete with an automatic table of contents per chapter. Open them in Google Play Books, Apple Books, Calibre, or any ebook reader app.

All download modes (combined, separate/zip, several chapters, single chapter) now support three formats: `.txt`, `.docx`, and `.epub`.

## v1.1.0

Resume, saved config, non-interactive mode, and the first release on PyPI.

### New features

- **Automatic resume.** Succeeded chapters are not downloaded again when the process stops midway.
- **Saved config.** The last save folder and file format are reused automatically in the next session.
- **Non-interactive mode.** Runs from command line arguments for scripting and automation.
- **Now on PyPI.** `pip install wattpdl`, then run `wattpdl` from any terminal.

### Improvements

- **src layout.** Code restructured to `src/wattpdl/` (standard Python packaging) so it can be published to PyPI.

## v1.0.0

First WattPDL release, the Wattpad Story Downloader.

### New features

- **4 download modes.** All chapters in one file, all chapters separate (`.zip`), several chapters, or one chapter.
- **2 output formats.** Plain `.txt` or `.docx`.
- **Interactive progress bar** with percentage and estimated time remaining.
- **Auto-retry.** Failed chapters are retried up to 3 times before being skipped.
- **No login.** Public Wattpad endpoint, no account needed.

### Improvements

- **Modular code.** Split into `api.py`, `writers.py`, and `cli.py` so it is easier to develop further.
- **Quality.** 29 unit tests (pytest), automatic linting via `ruff`, and CI (GitHub Actions) on every push and PR.
