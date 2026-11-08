# Changelog

All notable changes to this project are documented in this file. The format follows the release notes; see [CHANGELOG.id.md](CHANGELOG.id.md) for the Bahasa Indonesia version.

## v1.6.0

Connection pooling for faster downloads, Pillow is now a declared dependency, and an internal cleanup.

### Improvements

- **Connection pooling.** HTTP requests now reuse TCP/TLS connections per thread instead of a fresh handshake per chapter, which speeds up long downloads, especially with `--workers`.
- **Pillow is now a declared dependency.** It was already used for PDF image processing but only arrived transitively through reportlab; `pip install wattpdl` now guarantees it.
- **Clearer chapter errors.** A chapter that is deleted or restricted (404/403 when fetching its text) now shows the same clear message style as the story-level errors.
- **Internal cleanup.** Shared HTTP session, deduplicated helpers, and tidied modules. Command-line behavior is unchanged.

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
