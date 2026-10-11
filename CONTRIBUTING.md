# Contributing to WattPDL

**English** | [Bahasa Indonesia](CONTRIBUTING.id.md)

Thanks for your interest in helping improve WattPDL! This guide is kept short so it is easy to follow.

## Project Structure

```
src/wattpdl/
├── __init__.py   # package metadata (__version__)
├── __main__.py   # entry point for `python -m wattpdl`
├── app.py        # program flow orchestration (main())
├── api.py        # communication with the Wattpad public API (story info & chapter text)
├── writers.py    # text conversion and writing .txt/.docx/.epub/.md/.pdf/.zip files
├── cli.py        # terminal display (rich), user interaction
├── cli_args.py   # command line argument parsing & validation (non-interactive mode)
├── config.py     # saves user preferences (save folder, format, language) in ~/.wattpdl/config.json
├── i18n.py       # translations for the CLI display text (en/id)
└── progress.py   # cache of successfully downloaded chapters, for the resume feature
tests/            # unit tests (pytest)
```

Simple rules:
- `api.py` must not know anything about the display (`rich`)
- `writers.py` must not make network requests
- `config.py` and `progress.py` must not know about the CLI, `rich`, or the network: they only read and write JSON
- `cli_args.py` must not contain business logic, only argument parsing & validation
- `i18n.py` is pure data plus small functions, and must not know about `rich`, the network, or the CLI
- Do not hardcode user-facing text in the code. Add a new key in `i18n.py` for **both languages** (`en` and `id`, with the same `{name}` placeholders), then use `t("your.key")`. A test makes sure both languages always stay complete.
- Imports between modules inside the package use relative imports (`from . import api`, not `import api`)

If a new feature needs several modules together, put the orchestration in `app.py`.

## Documentation and Style

- Documentation is **English by default** (`README.md`, `CONTRIBUTING.md`). Indonesian versions live in `README.id.md` and `CONTRIBUTING.id.md`. When you change one, update the other.
- Write code comments, docstrings, commit messages, and test descriptions in English.
- Do not use em dashes in documents or code. Use a comma, a colon, or a hyphen instead.

## Local Setup

```bash
git clone https://github.com/nekonaru/wattpdl.git
cd wattpdl
pip install -e .[dev]
```

`pip install -e .[dev]` installs the project in "editable" mode (code changes take effect without reinstalling) together with the development dependencies (`pytest`, `ruff`, `build`, `twine`). After this, the `wattpdl` command in your terminal runs the code from this folder.

## Before Opening a Pull Request

1. **Run the tests** and make sure they all pass:
   ```bash
   pytest tests/ -v
   ```
2. **Run the linter** and make sure there are no warnings:
   ```bash
   ruff check .
   ```
3. If you add a new function that can be tested without an internet connection (parsing, formatting, validation), add its unit test in `tests/test_wattpdl.py`.
4. Update `README.md` (English) **and** `README.id.md` (Indonesian) if usage changes or a new feature is added.

## Contribution Flow

1. Fork this repo
2. Create a new branch: `git checkout -b feat/your-feature-name`
3. Commit your changes with a clear message (`feat: ...`, `fix: ...`, `docs: ...`, `test: ...`)
4. Push to your fork, then open a Pull Request to the `main` branch
5. Wait for GitHub Actions (test + lint) to finish and turn all green

## Reporting Bugs

Open a [new Issue](https://github.com/nekonaru/wattpdl/issues/new) and include:
- The Python version you use
- The command/steps you ran
- The full error message (if any)
- The story ID or link you used (if the bug is specific to a certain story, but make sure the story is public)

## Release Process (for maintainers)

1. Update the version number in **two places** (they must match):
   - `src/wattpdl/__init__.py` → `__version__ = "x.y.z"`
   - `pyproject.toml` → `version = "x.y.z"`
2. Commit the version change and push to `main`
3. Create a new **GitHub Release** with the tag `vx.y.z`
4. Publish the release → the `.github/workflows/publish.yml` workflow runs automatically, builds the package, and uploads it to PyPI through Trusted Publishing
5. Check `https://pypi.org/project/wattpdl/`, the new version should appear within a few minutes

Trusted Publishing must be registered once in the PyPI project settings page (Publishing → Add a new publisher) before this workflow can run. See [docs.pypi.org/trusted-publishers](https://docs.pypi.org/trusted-publishers/).
