<div align="center">
  <img src="assets/logo.png" alt="WattPDL logo" width="120" />
  <h1>WattPDL: Wattpad Story Downloader</h1>
  <p><b>Download Wattpad stories as offline .txt, .docx, .epub, .md, or .pdf files,<br/>
  whole or chapter by chapter, with no login or API key.</b></p>

  <a href="https://github.com/nekonaru/wattpdl/releases"><img src="https://img.shields.io/github/v/release/nekonaru/wattpdl?style=flat-square&color=blue" alt="Release" /></a>
  <a href="https://github.com/nekonaru/wattpdl/actions/workflows/tests.yml"><img src="https://github.com/nekonaru/wattpdl/actions/workflows/tests.yml/badge.svg" alt="CI" /></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.9+" />
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square" alt="Platform" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License" />
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square" alt="Status" />
</div>

<br />

**English** | [Bahasa Indonesia](README.id.md)

> [!NOTE]
> WattPDL is only for reading your own or publicly available stories offline. Respect the authors' copyright: do not redistribute or sell downloaded stories.

---

## Table of Contents

- [About](#about)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Display Language](#display-language)
- [Data Sources](#data-sources)
- [Project Structure](#project-structure)
- [Development](#development)
- [Testing](#testing)
- [Continuous Integration](#continuous-integration)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Author](#author)
- [Disclaimer](#disclaimer)
- [License](#license)

---

## About

**WattPDL** is a lightweight Python script that downloads the chapters of a Wattpad story of your choice and saves them as a clean, tidy plain `.txt` file, a Word `.docx` document, an `.epub` ebook, a Markdown `.md` file, or a `.pdf`. You can download the whole story as a single file, every chapter separately in one `.zip`, or only the chapters you pick, complete with the story cover automatically embedded in `.docx`/`.epub`/`.pdf`. No login, no API key, just the story link or ID.

> _"Because a good story deserves to be read anytime, even without internet."_

---

## Features

### Download Modes

| Feature | Description |
|---------|-------------|
| **4 download modes** | Everything in 1 file, everything separate in a `.zip`, pick several chapters, or just 1 chapter |
| **Download by author** | `--user <username>` downloads all or selected stories from one author at once |
| **Non-interactive mode** | Run with command line arguments for scripting/automation, no prompts to answer |
| **Automatic resume** | If the process stops midway, run the same story again: chapters that already succeeded are not downloaded again |
| **Skip existing files** | Skip the download if the output file already exists in the target folder, so nothing is overwritten by accident |

### Formats and Output

| Feature | Description |
|---------|-------------|
| **5 file formats** | Save as plain `.txt`, Word `.docx`, `.epub` ebook, Markdown `.md`, or `.pdf` |
| **Automatic cover** | The story cover is embedded in `.docx`/`.epub`/`.pdf` files (can be turned off with `--no-cover`) |
| **Inline images** | Optional (`--include-images`) download & embed of images inside chapter text, not just the cover. Very tall images (webtoon/comic strips) are sliced across PDF pages so they stay readable |
| **Rich EPUB metadata** | Genre/tags, story description, and publish date are saved as book metadata |
| **`--lang`** | Sets the EPUB metadata language code (default `id`) for stories in other languages |
| **Source link saved** | The story URL is included in the header of the resulting file |
| **Safe file names** | Illegal characters are removed from file names automatically |
| **Choose the save folder** | Defaults to the system `Downloads` folder, customizable |

### Reliability and Performance

| Feature | Description |
|---------|-------------|
| **No login** | Uses Wattpad's public endpoint, so no account is needed |
| **Auto-retry** | A failed chapter is retried up to 3 times before being skipped |
| **Parallel download** | `--workers N` downloads several chapters at once, speeding up long stories significantly |
| **Adaptive rate limit** | The delay between chapters slows down automatically when Wattpad starts limiting requests (429/503), then gradually speeds up again |
| **Metadata cache** | Story info is cached briefly so repeated attempts in a short time do not always hit the API |
| **Specific error messages** | Different messages for a deleted story (404) vs a private/restricted one (403) |

### Automation

| Feature | Description |
|---------|-------------|
| **New chapter detection** | `--check-updates` reports which ongoing stories already have new chapters |
| **Watch mode** | `--watch` monitors 1 story continuously and re-downloads as soon as a new chapter appears |
| **wattpdl update check** | Notifies you automatically when a newer wattpdl version is on PyPI |

### Interface and Experience

| Feature | Description |
|---------|-------------|
| **Neat CLI display** | Panels, story info tables, and colors thanks to the `rich` library |
| **English and Indonesian UI** | The CLI is in English by default; switch with `--ui-lang id` (menus, messages, and `--help`) |
| **Animated progress bar** | Spinner, percentage, chapter count, and estimated time remaining |
| **Final summary** | A report panel listing failed chapters (if any) when finished |
| **Remembers preferences** | The last save folder, file format, and language are reused in the next session |

---

## Requirements

| Dependency | Minimum Version | Notes |
|------------|-----------------|-------|
| **Python** | 3.9 | Runtime; Windows, macOS, or Linux |
| **Internet connection** | - | Required to reach Wattpad's public API |
| **requests** | 2.31 | HTTP client |
| **rich** | 13.7 | Terminal display |
| **python-docx** | 1.1 | `.docx` output |
| **EbookLib** | 0.18 | `.epub` output |
| **reportlab** | 4.0 | `.pdf` output |

The libraries are installed automatically together with `wattpdl`, no manual install needed.

> [!TIP]
> If you only want to use wattpdl, you do not need to install the libraries by hand. `pip install wattpdl` pulls in everything.

### Never used a terminal? Start here

<details>
<summary><b>How to open a terminal on Windows</b></summary>

1. Press the **Windows** key, type `PowerShell`, then press **Enter**
2. A black/blue window opens. That is where you type commands
3. Every `python ...` or `pip ...` command in this guide is typed in that window, followed by **Enter**

</details>

<details>
<summary><b>How to open a terminal on macOS</b></summary>

1. Press **Cmd + Space**, type `Terminal`, then press **Enter**
2. Type the commands from this guide there, followed by **Enter**

</details>

<details>
<summary><b>How to open a terminal on Linux</b></summary>

Press **Ctrl + Alt + T**, or search for the "Terminal" app in your application menu.

</details>

### Don't have Python yet?

1. Go to [python.org/downloads](https://www.python.org/downloads/) and download the latest version
2. **Windows only**: during installation, tick the **"Add Python to PATH"** box on the first screen before clicking Install. If you miss this, the `python` command will not be recognized later
3. After installing, open a terminal (see the guide above) and check with:

```bash
python --version
# or
python3 --version
```

If a version number appears (for example `Python 3.12.1`), you are ready.

---

## Installation

### Option A: Install from PyPI (easiest)

1. Open a terminal (see [Never used a terminal? Start here](#never-used-a-terminal-start-here))
2. Install wattpdl:

```bash
pip install wattpdl
```

3. Verify the install:

```bash
wattpdl --version
```

> If `pip` is not recognized, try:
> ```bash
> python -m pip install wattpdl
> ```

> If you get an `externally-managed-environment` error (usually on Linux):
> ```bash
> pip install wattpdl --break-system-packages
> ```

Once installed, the `wattpdl` command works from any terminal. Continue to [Usage](#usage).

### Option B: Build from source (for development / to read or change the code)

#### 1. Get the project code

<details>
<summary><b>I have Git installed</b></summary>

```bash
git clone https://github.com/nekonaru/wattpdl.git
cd wattpdl
```

</details>

<details>
<summary><b>I don't have Git</b></summary>

1. Open the repository page on GitHub
2. Click the green **`Code`** button, choose **`Download ZIP`**
3. Extract the downloaded ZIP file to a folder of your choice
4. In the terminal, go into the extracted folder, for example:

```bash
cd Downloads/wattpdl-main
```

</details>

#### 2. Install dependencies and verify

```bash
pip install -e .
wattpdl --version
```

> Same as Option A, add `--break-system-packages` at the end if you get an `externally-managed-environment` error.

This also registers the `wattpdl` command, but it loads the code directly from this folder, which is ideal if you want to modify the code and see the result right away without reinstalling.

#### 3. Run the tests

```bash
pip install -e .[dev]
pytest tests/ -v
ruff check .
```

### Option C: Arch Linux (AUR)

Arch Linux users can install it from the AUR. The package is community maintained by [@Vaishnav-Sabari-Girish](https://github.com/Vaishnav-Sabari-Girish): [`wattpdl` on the AUR](https://aur.archlinux.org/packages/wattpdl).

```bash
# Using yay
yay -S wattpdl

# Using paru
paru -S wattpdl
```

> The AUR package is maintained separately, so a new version may show up there a little after the PyPI release.

---

## Usage

### First launch

1. Run:

```bash
wattpdl
```

2. Enter the story link or ID when asked:

```
Wattpad story link or ID: https://www.wattpad.com/story/123456789-story-title
```

or just the ID:

```
Wattpad story link or ID: 123456789
```

The story ID is the number in the Wattpad URL, right after `/story/`.

3. Choose the download mode:

```
  1  All chapters -> 1 combined file
  2  All chapters -> separate file per chapter, packed as .zip
  3  Select several chapters -> 1 combined file
  4  Select 1 chapter only

Select mode [1/2/3/4] (1):
```

- **Mode 1**: the most common way, the whole story as one tidy file from the first to the last chapter
- **Mode 2**: good if you want to read chapter by chapter, producing one `.zip` with a file per chapter
- **Mode 3**: a numbered list of all chapter titles appears, then type the numbers you want, combining commas and ranges, for example: `1,3,5-8`
- **Mode 4**: a list of all chapter titles appears, type a single number to download only that chapter

4. Choose the file format:

```
  1  Plain text (.txt)
  2  Word document (.docx)
  3  Ebook (.epub)
  4  Markdown (.md)
  5  PDF (.pdf)

Select file format [1/2/3/4/5] (1):
```

5. Choose the save folder:

```
Default folder: C:\Users\user\Downloads
Press Enter to use that folder, or type another path:
```

Press **Enter** to save in `Downloads`, or type a custom path such as:

- Windows: `D:\Stories\Wattpad`
- Linux/macOS: `/home/user/stories`

6. Wait for it to finish:

```
⠋ Chapter 24...              ████████████████░░░░░░░░░░░░░░  53.3%  24/45  0:00:12  left 0:00:11
```

7. When it finishes, a summary panel is shown with the path of the saved file and the number of succeeded chapters (for example `45/45`). If some chapters failed, the panel lists them.

> [!NOTE]
> The CLI display is in English by default. Run `wattpdl --ui-lang id` once to switch to Bahasa Indonesia; the choice is remembered for next runs (see [Display Language](#display-language)). If you installed from source without `pip install -e .`, run `python -m wattpdl` from inside the `src/` folder instead.

### Everyday use

- Download a whole story as one `.epub` for the most comfortable reading in ebook apps
- Download a long story in Mode 2 to read it chapter by chapter, or use `--workers` to speed it up
- Schedule `--mode 1 --skip-existing` with cron or Task Scheduler for ongoing stories you re-download often
- Use `--check-updates` to see which downloaded ongoing stories have new chapters
- Use `--watch` to re-download automatically as soon as a new chapter appears

### Output structure

The name and shape of the generated files depend on the mode & format you choose:

| Mode | `.txt` format | `.docx` format | `.epub` format | `.md` format | `.pdf` format |
|------|----------------|-----------------|------------------|---------------|---------------|
| 1 - All, combined | `Story_Title.txt` | `Story_Title.docx` | `Story_Title.epub` | `Story_Title.md` | `Story_Title.pdf` |
| 2 - All, separate | `Story_Title.zip` (contains: one `.txt` per chapter) | `Story_Title.zip` (contains: one `.docx` per chapter) | `Story_Title.zip` (contains: one `.epub` per chapter) | `Story_Title.zip` (contains: one `.md` per chapter) | `Story_Title.zip` (contains: one `.pdf` per chapter) |
| 3 - Several chapters | `Story_Title_selected.txt` | `Story_Title_selected.docx` | `Story_Title_selected.epub` | `Story_Title_selected.md` | `Story_Title_selected.pdf` |
| 4 - One chapter | `Story_Title_Ch003_Chapter_Name.txt` | `Story_Title_Ch003_Chapter_Name.docx` | `Story_Title_Ch003_Chapter_Name.epub` | `Story_Title_Ch003_Chapter_Name.md` | `Story_Title_Ch003_Chapter_Name.pdf` |

**Content of the combined file (modes 1 & 3):** the story title, author, and source at the top, then each chapter separated by a `#####` marker.

```
Story Title
by Author Name
Source: https://www.wattpad.com/story/123456789

==================================================

##### Chapter 1 Title #####

Text of chapter 1...

##### Chapter 2 Title #####

Text of chapter 2...
```

In the `.docx` version, the story title becomes the main heading and each chapter automatically becomes a Heading 1 on a new page, so it is comfortable to read right away in Word or Google Docs.

In the `.epub` version, the story becomes a standard ebook with an automatic table of contents per chapter, ready to open in your favorite ebook reader (Google Play Books, Apple Books, Calibre, and others).

In the `.md` version, the story is written with standard Markdown headings (`#` for the title, `##` per chapter), which is pleasant to open in any editor or render directly on GitHub/Obsidian/Notion.

If the story has a cover, the image is embedded automatically on the first page/paragraph of the `.docx`/`.epub`/`.pdf` file (unless run with `--no-cover`). The story's genre/tags, description, and publish date are also saved as official metadata in the `.epub` file, usually shown on the book detail page in ebook reader apps.

**Zip content (mode 2):** one file per chapter, numbered by its position in the story, plus `000_info.txt`/`000_info.md`/`000_info.docx`/`000_info.epub`/`000_info.pdf` (matching the format) containing the title, author, and source. The file extension inside the zip follows the format you chose when running the script:

```
Story_Title.zip
├── 000_info.txt
├── 001_Chapter_1_Title.txt
├── 002_Chapter_2_Title.txt
└── ...
```

### Default save folder per OS

| Operating System | Default Folder |
|------------------|----------------|
| Windows | `C:\Users\<username>\Downloads` |
| macOS | `/Users/<username>/Downloads` |
| Linux | `/home/<username>/Downloads` |

### Automatic resume

If the download stops midway (connection lost, terminal closed, laptop shut down), every chapter that **already succeeded** is saved automatically in `~/.wattpdl/progress/<story_id>.json`.

Run again with the same story (same ID/link), and WattPDL will:

- Skip chapters that already succeeded (used from the cache, not fetched again)
- Download only the chapters that have not succeeded yet or failed earlier

The progress file is deleted automatically once all chapters have been downloaded in a single session. To force a download from scratch, delete the `~/.wattpdl/progress/` folder manually.

> **Not the same as `--skip-existing`:** the resume above works at the *chapter* level (continuing a download that stopped midway). `--skip-existing` works at the *output file* level: if the final file (for example `Story_Title.epub`) already exists in the target folder, the whole download is skipped entirely, which is handy together with `cron`/Task Scheduler so stories that were already downloaded are not downloaded again.

### Saved preferences

The last save folder, file format, and display language you chose are saved automatically in `~/.wattpdl/config.json` and reused as defaults in the next session, so there is no need to fill them in every time you run the script.

### Non-interactive mode (scripting/automation)

Besides the question-and-answer mode, WattPDL can also be run through command line arguments, which is great for scheduling (cron/Task Scheduler) or calling from other scripts.

```bash
wattpdl --id 398440633 --mode 1 --format docx
```

**Available arguments:**

| Argument | Description |
|---|---|
| `--id` | Wattpad story ID or link. Setting this enables non-interactive mode. |
| `--mode {1,2,3,4}` | 1 = everything in 1 file, 2 = everything separate in a `.zip`, 3 = select several chapters, 4 = select 1 chapter |
| `--format {txt,docx,epub,md,pdf}` | Output file format. Default: from saved config, or `txt` |
| `--chapters` | Chapter numbers for `--mode 3`, example: `1,3,5-8` |
| `--chapter` | Chapter number for `--mode 4`, example: `5` |
| `--output-dir` | Custom save folder. Default: from saved config, or the `Downloads` folder |
| `--skip-existing` | Skip the download if the target output file already exists, instead of overwriting it |
| `--no-cover` | Do not embed the story cover image in `.docx`/`.epub`/`.pdf` files |
| `--include-images` | Also download & embed inline images inside chapters (adds download time) |
| `--workers N` | Number of chapters downloaded at the same time (default 1) |
| `--no-cache` | Do not use the story metadata cache, always fetch fresh data |
| `--lang` | ISO 639-1 language code for EPUB metadata (default `id`) |
| `--ui-lang {id,en}` | CLI display language (default `en`, remembered once chosen) |
| `--user` / `--user-select` | Download from an author's story list, optionally selecting which stories |
| `--check-updates` | Report which downloaded stories have new chapters |
| `--watch` / `--watch-interval` | Monitor a story and re-download when new chapters appear (default check interval 1800 seconds) |
| `--no-update-check` | Do not check for the latest wattpdl version on PyPI at startup |
| `--version` | Show the wattpdl version |

**More examples:**

```bash
# Download all chapters as separate files in a .zip
wattpdl --id 398440633 --mode 2 --format txt

# Download only chapters 1, 3, and 5-8 as 1 combined file
wattpdl --id 398440633 --mode 3 --chapters 1,3,5-8 --format docx

# Download only chapter 10, save to a custom folder
wattpdl --id 398440633 --mode 4 --chapter 10 --output-dir "D:\Wattpad Stories"

# Download all chapters as 1 .epub ebook
wattpdl --id 398440633 --mode 1 --format epub

# Download as Markdown, skip if the file already exists (good for scheduling)
wattpdl --id 398440633 --mode 1 --format md --skip-existing

# Show all options
wattpdl --help
```

---

## Display Language

The CLI display (menus, prompts, error messages, and `--help` text) is available in **English** (default) and **Indonesian**.

1. Switch the display language once:

```bash
wattpdl --ui-lang id              # Indonesian, this choice is remembered for next runs
wattpdl --ui-lang en              # back to English
```

2. Or set it through an environment variable:

```bash
WATTPDL_LANG=id wattpdl
```

Priority order: `--ui-lang` -> env `WATTPDL_LANG` -> `ui_lang` in `~/.wattpdl/config.json` -> default `en`.

> `--ui-lang` only changes the CLI display. Do not confuse it with `--lang`, which sets the language code in the EPUB metadata.

---

## Data Sources

WattPDL talks to public endpoints only. No login or API key is needed.

| Purpose | Source |
|---------|--------|
| Story metadata (title, author, chapter list, genres, description, publish date) | Wattpad public API v3 (`wattpad.com/api/v3`) |
| Chapter text | Wattpad public story text endpoint (`wattpad.com/apiv2/storytext`) |
| Author story list (`--user`) | Wattpad public API v3 (`wattpad.com/api/v3/users/{username}/stories/published`) |
| wattpdl update check | PyPI JSON API (`pypi.org/pypi/wattpdl/json`) |

> [!NOTE]
> These are public endpoints, the same ones your browser uses when you read a story on wattpad.com. Access is read-only, and no account or cookie is sent.

---

## Project Structure

```
wattpdl/
├── assets/
│   └── logo.png             # project logo, used in the README
├── src/
│   └── wattpdl/
│       ├── __init__.py       # package metadata (__version__)
│       ├── __main__.py       # entry point for `python -m wattpdl`
│       ├── app.py            # program flow orchestration (main())
│       ├── api.py            # communication with the Wattpad public API
│       ├── writers.py        # text conversion & writing .txt/.docx/.epub/.md/.pdf/.zip files
│       ├── cli.py            # terminal display (rich), user interaction
│       ├── cli_args.py       # argument parsing for non-interactive mode
│       ├── config.py         # saves user preferences (save folder, format, language)
│       ├── i18n.py           # CLI display translations (en/id)
│       ├── library.py        # local library of downloaded stories (used by --check-updates)
│       ├── metacache.py      # short-lived cache of story metadata
│       ├── updater.py        # wattpdl update check on PyPI
│       └── progress.py       # download progress cache for the resume feature
├── requirements.txt          # dependency list (for manual reference)
├── pyproject.toml            # package metadata + build config + ruff
├── tests/
│   ├── __init__.py
│   └── test_wattpdl.py       # unit tests (pytest)
├── .github/
│   └── workflows/
│       ├── tests.yml         # CI: automatic test, lint, & build check
│       └── publish.yml       # auto-publish to PyPI on a new release
├── CHANGELOG.md              # version history (English)
├── CHANGELOG.id.md           # version history (Bahasa Indonesia)
├── CONTRIBUTING.md           # contribution guide (English)
├── CONTRIBUTING.id.md        # contribution guide (Bahasa Indonesia)
├── SECURITY.md               # vulnerability reporting policy
├── LICENSE
├── README.md                 # main documentation (English)
└── README.id.md              # documentation (Bahasa Indonesia)
```

**Module separation principles:**

- `api.py`: knows nothing about the display (`rich`), purely fetches data
- `writers.py`: makes no network requests, purely converts & writes files
- `cli.py`: all user interaction & progress bar display
- `cli_args.py`: command line argument parsing & validation, no business logic
- `i18n.py`: display text dictionary (English/Indonesian), pure data, knows nothing about `rich` or the network
- `config.py` / `progress.py`: read/write JSON files in `~/.wattpdl/`, know nothing about the CLI or the network
- `app.py`: ties everything together, with no business logic of its own (invoked through the `wattpdl` command after install)

---

## Development

Built with Python, `requests`, `rich`, `python-docx`, `EbookLib`, and `reportlab`.

### Adding a new user-facing string

1. Add the English and Indonesian strings next to each other in `src/wattpdl/i18n.py`
2. Use `t("your_key")` in the code, never a raw string literal
3. Run the tests; the test suite checks that both languages always have the same keys and placeholders

### Keeping the docs in sync

1. Update `README.md` first, then `README.id.md`, in the same commit
2. Use the exact same section order, tables, and callouts in both files
3. If the release changes user-facing behavior, update `CHANGELOG.md` and `CHANGELOG.id.md` too

Want to help? Read [`CONTRIBUTING.md`](CONTRIBUTING.md) for the project structure and contribution flow.

---

## Testing

There are unit tests for the core functions (story ID parsing, file name validation, chapter selection parsing, HTML to text conversion, config, progress/resume, CLI argument parsing, translations, and more).

```bash
pip install -e .[dev]
pytest tests/ -v
ruff check .
```

| Check | Requirement |
|-------|-------------|
| `pytest tests/ -v` | Must pass the full suite |
| `ruff check .` | Must report zero issues |

Lint rules live in `pyproject.toml` under `[tool.ruff]` (line-length 110, target Python 3.9).

---

## Continuous Integration

| Workflow | Purpose |
|----------|---------|
| `tests.yml` | ruff lint, pytest on Python 3.9-3.12, and a package build with `twine check` on every push and pull request to `main` |
| `publish.yml` | builds and publishes to PyPI via trusted publishing (OIDC) when a GitHub Release is published |

Lint, tests, and the build check must be green before every push. Publishing to PyPI happens only through a published GitHub Release.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'requests'` | Run `pip install requests` |
| `ModuleNotFoundError: No module named 'rich'` | Run `pip install rich` |
| `Library 'python-docx' is not installed` | Run `pip install python-docx` (only needed if you choose the `.docx` format) |
| `Library 'EbookLib' is not installed` | Run `pip install EbookLib` (only needed if you choose the `.epub` format) |
| `Library 'reportlab' is not installed` | Run `pip install reportlab` (only needed if you choose the `.pdf` format) |
| `404` error / "No chapters found" | Make sure the ID/link is correct & the story is not private |
| Folder cannot be created | Check that the path is valid & you have write permission there |
| The process hangs on one chapter | Check your internet connection and run again, progress will continue |

---

## FAQ

<details>
<summary><b>Is this legal / safe to use?</b></summary>

This script uses the same public Wattpad endpoint as when you read a story in the browser, so it does not hack anything. But use it responsibly: download for personal/offline reading, and respect the authors' copyright. Do not redistribute or sell other people's stories.

</details>

<details>
<summary><b>Do I need a Wattpad account?</b></summary>

No. No login or API key is needed at all.

</details>

<details>
<summary><b>Can I download private / deleted stories?</b></summary>

No. The script can only access stories that are public.

</details>

<details>
<summary><b>Why does it take so long?</b></summary>

There is a 0.5 second delay between chapters (on purpose, so Wattpad's servers are not overloaded). For stories with hundreds of chapters, it is normal for the process to take a few minutes. You can speed it up with `--workers`.

</details>

<details>
<summary><b>Which mode and format should I pick?</b></summary>

- Want to read from start to finish like a book: **Mode 1**, the `.epub` format is the most comfortable in ebook apps
- Want each chapter as its own file: **Mode 2**
- Only need a few specific chapters (for example re-reading a certain part): **Mode 3**
- Just curious about one chapter: **Mode 4**
- Want to read casually on a phone/tablet with an ebook app (Google Play Books, Apple Books, etc.): choose the **`.epub`** format
- Want to edit or print neatly with Word: choose the **`.docx`** format
- Want a small, simple file, or to read it in an e-reader/notes app: choose the **`.txt`** format

</details>

---

## Author

<div align="center">

| [![Nicolas Dwi Dharma](https://github.com/nekonaru.png?size=100)](https://github.com/nekonaru) |
|:---:|
| **Nicolas Dwi Dharma** |
| [github.com/nekonaru](https://github.com/nekonaru) |

</div>

---

## Disclaimer

WattPDL is an independent open-source project and is not affiliated with or endorsed by Wattpad. It reads publicly available story data through Wattpad's public endpoints, for personal offline reading only. Respect the authors' copyright: do not redistribute, upload, or sell downloaded stories.

---

## License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.
