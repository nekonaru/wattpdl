<div align="center">
  <h1>WattPDL: Wattpad Story Downloader</h1>
  <p><b>Save your favorite stories as <code>.txt</code>, <code>.docx</code>, <code>.epub</code>, <code>.md</code>, or <code>.pdf</code> files,<br/>
  whole or chapter by chapter, for offline reading.</b></p>

  <a href="https://pypi.org/project/wattpdl/"><img src="https://img.shields.io/pypi/v/wattpdl?style=flat-square&color=blue" alt="PyPI" /></a>
  <a href="https://github.com/nekonaru/wattpdl/actions/workflows/tests.yml"><img src="https://github.com/nekonaru/wattpdl/actions/workflows/tests.yml/badge.svg" alt="Tests" /></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square" alt="Platform" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License" />
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square" alt="Status" />
</div>

<br />

**English** | [Bahasa Indonesia](https://github.com/nekonaru/wattpdl/blob/main/README.id.md)

> [!CAUTION]
> This script is only for reading your own stories or public stories offline. Respect the authors' copyright. Do not redistribute or sell other people's stories.

---

## Table of Contents

- [About](#about)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Automatic Resume](#automatic-resume)
- [Saved Preferences](#saved-preferences)
- [Display Language](#display-language)
- [Non-Interactive Mode (Scripting/Automation)](#non-interactive-mode-scriptingautomation)
- [Output Structure](#output-structure)
- [Default Folder per OS](#default-folder-per-os)
- [Troubleshooting](#troubleshooting)
- [Important Notes](#important-notes)
- [Built With](#built-with)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Continuous Integration](#continuous-integration)
- [Contributing](#contributing)
- [FAQ](#faq)
- [Author](#author)
- [License](#license)

---

## About

**WattPDL** is a lightweight Python script that downloads the chapters of a Wattpad story of your choice and saves them as a clean, tidy plain `.txt` file, a Word `.docx` document, an `.epub` ebook, a Markdown `.md` file, or a `.pdf`. You can download the whole story as a single file, every chapter separately in one `.zip`, or only the chapters you pick, complete with the story cover automatically embedded in `.docx`/`.epub`/`.pdf`. No login, no API key, just the story link or ID.

> _"Because a good story deserves to be read anytime, even without internet."_

---

## Features

### Downloading

| Feature | Description |
|---------|-------------|
| **4 download modes** | Everything in 1 file, everything separate in a `.zip`, pick several chapters, or just 1 chapter |
| **5 file formats** | Save as plain `.txt`, Word `.docx`, `.epub` ebook, Markdown `.md`, or `.pdf` |
| **No login** | Uses Wattpad's public endpoint, so no account is needed |
| **Download by author** | `--user <username>` downloads all or selected stories from one author at once |
| **Choose the save folder** | Defaults to the system `Downloads` folder, customizable |
| **Skip existing files** | Skip the download if the output file already exists in the target folder, so nothing is overwritten by accident |
| **Safe file names** | Illegal characters are removed from file names automatically |

### Output Content

| Feature | Description |
|---------|-------------|
| **Automatic cover** | The story cover is embedded in `.docx`/`.epub`/`.pdf` files (can be turned off with `--no-cover`) |
| **Inline images** | Optional (`--include-images`) download & embed of images inside chapter text, not just the cover. Very tall images (webtoon/comic strips) are sliced across PDF pages so they stay readable |
| **Rich EPUB metadata** | Genre/tags, story description, and publish date are saved as book metadata |
| **Source link saved** | The story URL is included in the header of the resulting file |
| **`--lang`** | Sets the EPUB metadata language code (default `id`) for stories in other languages |

### Reliability and Speed

| Feature | Description |
|---------|-------------|
| **Auto-retry** | A failed chapter is retried up to 3 times before being skipped |
| **Automatic resume** | If the process stops midway, run the same story again: chapters that already succeeded are not downloaded again |
| **Parallel download** | `--workers N` downloads several chapters at once, speeding up long stories significantly |
| **Adaptive rate limit** | The delay between chapters slows down automatically when Wattpad starts limiting requests (429/503), then gradually speeds up again |
| **Metadata cache** | Story info is cached briefly so repeated attempts in a short time do not always hit the API |
| **Specific error messages** | Different messages for a deleted story (404) vs a private/restricted one (403) |

### Interface

| Feature | Description |
|---------|-------------|
| **Neat CLI display** | Panels, story info tables, and colors thanks to the `rich` library |
| **English and Indonesian UI** | The CLI is in English by default; switch with `--ui-lang id` (menus, messages, and `--help`) |
| **Animated progress bar** | Spinner, percentage, chapter count, and estimated time remaining |
| **Final summary** | A report panel listing failed chapters (if any) when finished |
| **Remembers preferences** | The last save folder, file format, and language are reused in the next session |

### Automation and Updates

| Feature | Description |
|---------|-------------|
| **Non-interactive mode** | Run with command line arguments for scripting/automation, no prompts to answer |
| **New chapter detection** | `--check-updates` reports which ongoing stories already have new chapters |
| **Watch mode** | `--watch` monitors 1 story continuously and re-downloads as soon as a new chapter appears |
| **wattpdl update check** | Notifies you automatically when a newer wattpdl version is on PyPI |

---

## Requirements

| Dependency | Minimum Version | Notes |
|------------|-----------------|-------|
| **Python** | 3.9 | Required |
| **Internet connection** | any | Required |
| **Libraries** | see notes | `requests`, `rich`, `python-docx`, `EbookLib`, `reportlab`, installed automatically together with `wattpdl`, no manual install needed |

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
2. **Windows only**: during installation, tick the **"Add Python to PATH"** box on the first screen before clicking Install
3. After installing, open a terminal (see the guide above) and check with:

```bash
python --version
# or
python3 --version
```

If a version number appears (for example `Python 3.12.1`), you are ready.

> [!WARNING]
> On Windows, if you miss the **"Add Python to PATH"** box during installation, the `python` command will not be recognized later.

---

## Installation

### Option A: Install from PyPI (easiest)

```bash
pip install wattpdl
```

> [!TIP]
> If `pip` is not recognized, try `python -m pip install wattpdl`.

> [!NOTE]
> If you get an `externally-managed-environment` error (usually on Linux), run:
> ```bash
> pip install wattpdl --break-system-packages
> ```

Once installed, the `wattpdl` command works from any terminal. Continue to [Usage](#usage).

### Option B: Install from source (for development / to read or change the code)

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
2. Click the green **`Code`** button, then choose **`Download ZIP`**
3. Extract the downloaded ZIP file to a folder of your choice
4. In the terminal, go into the extracted folder, for example:

```bash
cd Downloads/wattpdl-main
```

</details>

#### 2. Install in "editable" mode

```bash
pip install -e .
```

> [!NOTE]
> Same as Option A, add `--break-system-packages` at the end if you get an `externally-managed-environment` error.

This also registers the `wattpdl` command, but it loads the code directly from this folder, which is ideal if you want to modify the code and see the result right away without reinstalling.

### Option C: Arch Linux (AUR)

Arch Linux users can install it from the AUR. The package is community maintained by [@Vaishnav-Sabari-Girish](https://github.com/Vaishnav-Sabari-Girish): [`wattpdl` on the AUR](https://aur.archlinux.org/packages/wattpdl).

```bash
# Using yay
yay -S wattpdl

# Using paru
paru -S wattpdl
```

> [!NOTE]
> The AUR package is maintained separately, so a new version may show up there a little after the PyPI release.

---

## Usage

**Run:**

```bash
wattpdl
```

> [!NOTE]
> If you installed from source without `pip install -e .`, run it with `python -m wattpdl` from inside the `src/` folder. The editable install above is recommended, though.

**Enter the story link or ID when asked:**

```
Wattpad story link or ID: https://www.wattpad.com/story/123456789-story-title
```

or just the ID:

```
Wattpad story link or ID: 123456789
```

**Choose the download mode:**

```
  1  All chapters → 1 combined file
  2  All chapters → separate file per chapter, packed as .zip
  3  Select several chapters → 1 combined file
  4  Select 1 chapter only

Select mode [1/2/3/4] (1):
```

| Mode | Description |
|------|-------------|
| **Mode 1** | The most common way, the whole story as one tidy file from the first to the last chapter |
| **Mode 2** | Good if you want to read chapter by chapter, producing one `.zip` with a file per chapter |
| **Mode 3** | A numbered list of all chapter titles appears, then type the numbers you want, combining commas and ranges, for example: `1,3,5-8` |
| **Mode 4** | A list of all chapter titles appears, type a single number to download only that chapter |

**Choose the file format:**

```
  1  Plain text (.txt)
  2  Word document (.docx)
  3  Ebook (.epub)
  4  Markdown (.md)
  5  PDF (.pdf)

Select file format [1/2/3/4/5] (1):
```

**Choose the save folder:**

```
Default folder: C:\Users\user\Downloads
Press Enter to use that folder, or type another path:
```

Press **Enter** to save in `Downloads`, or type a custom path such as:
- Windows: `D:\Stories\Wattpad`
- Linux/macOS: `/home/user/stories`

**Wait for it to finish:**

```
⠋ Chapter 24...              ████████████████░░░░░░░░░░░░░░  53.3%  24/45  0:00:12  left 0:00:11
```

**Done!**

```
╔═════════════ Success!  All chapters saved ══════════════╗
║ File saved to   C:\Users\user\Downloads\Story_Title.txt ║
║ Succeeded       45/45                                   ║
║ Total time      2m 18s                                  ║
╚═════════════════════════════════════════════════════════╝
```

---

## Automatic Resume

If the download stops midway (connection lost, terminal closed, laptop shut down), every chapter that **already succeeded** is saved automatically in `~/.wattpdl/progress/<story_id>.json`.

Run again with the same story (same ID/link), and WattPDL will:
- Skip chapters that already succeeded (used from the cache, not fetched again)
- Download only the chapters that have not succeeded yet or failed earlier

The progress file is deleted automatically once all chapters have been downloaded in a single session. To force a download from scratch, delete the `~/.wattpdl/progress/` folder manually.

> [!NOTE]
> **Not the same as `--skip-existing`:** the resume above works at the *chapter* level (continuing a download that stopped midway). `--skip-existing` works at the *output file* level: if the final file (for example `Story_Title.epub`) already exists in the target folder, the whole download is skipped entirely, which is handy together with `cron`/Task Scheduler so stories that were already downloaded are not downloaded again.

---

## Saved Preferences

The last save folder, file format, and display language you chose are saved automatically in `~/.wattpdl/config.json` and reused as defaults in the next session, so there is no need to fill them in every time you run the script.

---

## Display Language

The CLI display (menus, prompts, error messages, and `--help` text) is available in **English** (default) and **Indonesian**.

```bash
wattpdl --ui-lang id              # Indonesian, this choice is remembered for next runs
wattpdl --ui-lang en              # back to English
WATTPDL_LANG=id wattpdl           # via environment variable
```

Priority order: `--ui-lang` → env `WATTPDL_LANG` → `ui_lang` in `~/.wattpdl/config.json` → default `en`.

> [!IMPORTANT]
> `--ui-lang` only changes the CLI display. Do not confuse it with `--lang`, which sets the language code in the EPUB metadata.

---

## Non-Interactive Mode (Scripting/Automation)

Besides the question-and-answer mode, WattPDL can also be run through command line arguments, which is great for scheduling (cron/Task Scheduler) or calling from other scripts.

```bash
wattpdl --id 398440633 --mode 1 --format docx
```

### Available arguments

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

### More examples

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

## Output Structure

The name and shape of the generated files depend on the mode & format you choose:

| Mode | `.txt` format | `.docx` format | `.epub` format | `.md` format | `.pdf` format |
|------|----------------|-----------------|------------------|---------------|---------------|
| 1 - All, combined | `Story_Title.txt` | `Story_Title.docx` | `Story_Title.epub` | `Story_Title.md` | `Story_Title.pdf` |
| 2 - All, separate | `Story_Title.zip` (contains: one `.txt` per chapter) | `Story_Title.zip` (contains: one `.docx` per chapter) | `Story_Title.zip` (contains: one `.epub` per chapter) | `Story_Title.zip` (contains: one `.md` per chapter) | `Story_Title.zip` (contains: one `.pdf` per chapter) |
| 3 - Several chapters | `Story_Title_selected.txt` | `Story_Title_selected.docx` | `Story_Title_selected.epub` | `Story_Title_selected.md` | `Story_Title_selected.pdf` |
| 4 - One chapter | `Story_Title_Ch003_Chapter_Name.txt` | `Story_Title_Ch003_Chapter_Name.docx` | `Story_Title_Ch003_Chapter_Name.epub` | `Story_Title_Ch003_Chapter_Name.md` | `Story_Title_Ch003_Chapter_Name.pdf` |

### Combined file content (modes 1 and 3)

The story title, author, and source at the top, then each chapter separated by a `#####` marker.

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

### Format details

| Format | Details |
|--------|---------|
| `.docx` | The story title becomes the main heading and each chapter automatically becomes a Heading 1 on a new page, so it is comfortable to read right away in Word or Google Docs. |
| `.epub` | The story becomes a standard ebook with an automatic table of contents per chapter, ready to open in your favorite ebook reader (Google Play Books, Apple Books, Calibre, and others). |
| `.md` | The story is written with standard Markdown headings (`#` for the title, `##` per chapter), which is pleasant to open in any editor or render directly on GitHub/Obsidian/Notion. |

If the story has a cover, the image is embedded automatically on the first page/paragraph of the `.docx`/`.epub`/`.pdf` file (unless run with `--no-cover`). The story's genre/tags, description, and publish date are also saved as official metadata in the `.epub` file, usually shown on the book detail page in ebook reader apps.

### Zip content (mode 2)

One file per chapter, numbered by its position in the story, plus `000_info.txt`/`000_info.md`/`000_info.docx`/`000_info.epub`/`000_info.pdf` (matching the format) containing the title, author, and source. The file extension inside the zip follows the format you chose when running the script:

```
Story_Title.zip
├── 000_info.txt
├── 001_Chapter_1_Title.txt
├── 002_Chapter_2_Title.txt
└── ...
```

---

## Default Folder per OS

| Operating System | Default Folder |
|------------------|----------------|
| Windows | `C:\Users\<username>\Downloads` |
| macOS | `/Users/<username>/Downloads` |
| Linux | `/home/<username>/Downloads` |

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

## Important Notes

- The story ID is the number in the Wattpad URL, right after `/story/`
- The script uses a public endpoint, no login or API key needed
- The **0.5 second** delay between chapters is set to avoid server rate limits, please do not remove it
- This script is only for reading your own stories or public stories offline. Respect the authors' copyright

---

## Built With

<div align="center">

![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Requests](https://img.shields.io/badge/-Requests-FF6B6B?style=flat-square)
![Rich](https://img.shields.io/badge/-Rich-FAE742?style=flat-square)
![python--docx](https://img.shields.io/badge/-python--docx-2B579A?style=flat-square)
![Wattpad API](https://img.shields.io/badge/-Wattpad%20Public%20API-FF6122?style=flat-square)

</div>

---

## Project Structure

```
wattpdl/
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
├── CONTRIBUTING.md           # contribution guide (English)
├── CONTRIBUTING.id.md        # contribution guide (Indonesian)
├── LICENSE
├── README.md                 # main documentation (English)
└── README.id.md              # documentation (Indonesian)
```

### Module separation principles

| Module | Principle |
|--------|-----------|
| `api.py` | Knows nothing about the display (`rich`), purely fetches data |
| `writers.py` | Makes no network requests, purely converts & writes files |
| `cli.py` | All user interaction & progress bar display |
| `cli_args.py` | Command line argument parsing & validation, no business logic |
| `i18n.py` | Display text dictionary (English/Indonesian), pure data, knows nothing about `rich` or the network |
| `config.py` / `progress.py` | Read/write JSON files in `~/.wattpdl/`, know nothing about the CLI or the network |
| `app.py` | Ties everything together, with no business logic of its own (invoked through the `wattpdl` command after install) |

---

## Testing

There are unit tests for the core functions (story ID parsing, file name validation, chapter selection parsing, HTML to text conversion, config, progress/resume, CLI argument parsing, translations, and more).

```bash
pip install -e .[dev]
pytest tests/ -v
ruff check .
```

---

## Continuous Integration

| Workflow | Purpose |
|----------|---------|
| `tests.yml` | Automatic test, lint, & build check |
| `publish.yml` | Auto-publish to PyPI on a new release |

---

## Contributing

Want to help improve WattPDL? Read [`CONTRIBUTING.md`](https://github.com/nekonaru/wattpdl/blob/main/CONTRIBUTING.md) for the project structure and contribution flow.

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

| [![Nicolas Dwi Dharma](https://github.com/github.png?size=100)](https://github.com/nekonaru) |
|:---:|
| **Nicolas Dwi Dharma** |
| [github.com/nekonaru](https://github.com/nekonaru) |

</div>

---

## License

Distributed under the **MIT License**. See [`LICENSE`](https://github.com/nekonaru/wattpdl/blob/main/LICENSE) for more information.
