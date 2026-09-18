# bible-translations

<p align=center>
  <a href="https://github.com/jadenzaleski/bible-translations/actions/workflows/ci.yml">
    <img alt="CI" src="https://img.shields.io/github/actions/workflow/status/jadenzaleski/bible-translations/ci.yml?branch=master&style=flat-square&label=CI">
  </a>
  <a href="https://github.com/jadenzaleski/bible-translations/actions/workflows/lint.yml">
    <img alt="Lint" src="https://img.shields.io/github/actions/workflow/status/jadenzaleski/bible-translations/lint.yml?branch=master&style=flat-square&label=lint">
  </a>
  <a href="https://github.com/jadenzaleski/bible-translations/releases/latest">
    <img alt="GitHub Release" src="https://img.shields.io/github/v/release/jadenzaleski/bible-translations?style=flat-square">
  </a>
  <a href="https://pypi.org/project/bible-translations/">
    <img alt="PyPI - Version" src="https://img.shields.io/pypi/v/bible-translations?style=flat-square">
  </a>
  <a href="https://pypi.org/project/bible-translations/">
    <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/bible-translations?style=flat-square">
  </a>
  <a href="https://pypi.org/project/bible-translations/">
    <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/bible-translations?style=flat-square">
  </a>
  <a href="LICENSE">
    <img alt="License" src="https://img.shields.io/github/license/jadenzaleski/bible-translations?style=flat-square">
  </a>
  <img alt="Github Created At" src="https://img.shields.io/github/created-at/jadenzaleski/bible-translations?style=flat-square&color=orange">
  <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/jadenzaleski/bible-translations?style=flat-square">
</p>

A Python package and CLI for fetching Bible translations on demand. This project does not
bundle or redistribute any Bible text — it fetches publicly available, public-domain
translations from [BibleGateway](https://www.biblegateway.com) at request time, either as
Python objects (via the API) or as exported JSON files (via the CLI).

## Documentation

Full API and CLI reference: https://jadenzaleski.github.io/bible-translations/

## Supported translations

| Translation | Abbreviation | Copyright     |
|-------------|--------------|---------------|
| KJV         | KJV          | Public Domain |
| ASV         | ASV          | Public Domain |

## Install

You can Install from PyPI

```bash
pip install bible-translations 
```

The package provides a CLI command:

```bash
bt
# or
bible-translations
```

### Install from local source

Clone the repo and install in editable mode:

```bash
git clone https://github.com/jadenzaleski/bible-translations.git
cd bible-translations
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -e ".[dev]"
```

The last command (`pip install -e ".[dev]"`) automatically installs the package *and* any tools listed under
`[project.optional-dependencies].dev` (e.g. `pytest`, `ruff`). The `-e` flag creates a "symlink" so changes you make to
`src/bible_translations/` are immediately available when importing the package.

### Build from a local source

Generate a wheel and source distribution:

```bash
python -m build
```

This creates a dist/ folder with:

- .whl → wheel (binary distribution)
- .tar.gz → source distribution

You can install the wheel to test locally:

```bash
pip install dist/bible_translations*.whl
```

### Run Tests

```bash
pip install pytest
pytest
```

## Usage

The package provides a CLI for fetching and exporting Bible translations.

### Examples

* **Fetch a verse:**
  ```bash
  bt verse "John 3:16"
  ```
* **Fetch a chapter:**
  ```bash
  bt chapter "John 3"
  ```
* **Fetch a book:**
  ```bash
  bt book John
  ```
* **Fetch all books:**
  ```bash
  bt books
  ```
* **Fetch a selection:**
  ```bash
  bt selection "John 3:16" "John 3:18"
  ```

### Options

In any command, you can specify the translation, output filename, and format:

* **Specify translation (default: KJV):**
  ```bash
  bt verse "John 3:16" --translation KJV
  # or
  bt verse "John 3:16" -t KJV
  ```
* **Specify output file and format (default: export, json):**
  ```bash
  bt verse "John 3:16" my_export json
  ```

## Changelog

You can find all the change information [here](CHANGELOG.md).

## Contributing

Be sure to check out the [bible-translations project](https://github.com/users/jadenzaleski/projects/7) to see where you
can help!

Guidelines for contributing can be found [here](CONTRIBUTING.md).

## Disclaimer

Please read our disclaimer [here](DISCLAIMER.md).

