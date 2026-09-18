# v1.0.0 Stable Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Take `bible-translations` from its current pre-alpha `development`-branch state to a fully working, tested, documented v1.0.0 released on PyPI, with a mostly-automated release pipeline (release-please + trusted-publisher PyPI CD) going forward.

**Architecture:** No architectural rewrite. This plan consolidates the existing `development` branch into `master` as the single trunk, fills in real functionality gaps (a second translation, a flatten API), removes duplicate/manual bookkeeping (version string, bundled-data messaging), hardens the test suite (network tests are currently unmocked and untagged), adds a documentation site, and wires up release-please + PyPI OIDC publishing so that merging Conventional-Commit PRs to `master` is the only manual step required to ship a release.

**Tech Stack:** Python 3.11+, Click, aiohttp, BeautifulSoup4, pytest + pytest-asyncio + pytest-rerunfailures, Ruff, GitHub Actions, release-please, mkdocs + mkdocs-material + mkdocstrings + mkdocs-click, PyPI Trusted Publishing (OIDC).

**Spec:** This plan is self-contained; there is no separate spec document. Product decisions locked in during planning (see Global Constraints) came from a live Q&A with the repo owner and are treated as binding requirements.

## Global Constraints

- `master` is the **only** trunk branch going forward. `development` is merged in and retired. All future work happens on short-lived branches PR'd into `master`.
- This package **never ships bundled/pre-fetched Bible text**, in the repo, in PyPI, or as release assets. It is a fetch-on-demand tool only (CLI + API). No "Download" table of precompiled translations in the README.
- Only public-domain translations are added (matches `DISCLAIMER.md`). v1.0.0 ships **KJV** (existing) + **ASV** (new, American Standard Version 1901, public domain, confirmed scrapable — see Task 6).
- v1.0.0 includes the "flatten" feature (GitHub issue #22). Paragraph-break metadata (issue #4) is explicitly **out of scope** — do not touch verse/chapter parsing to add paragraph boundaries.
- All commits and PR titles must use **Conventional Commits** (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`, `ci:`, `build:`, `perf:`) — release-please's version bumps and changelog depend on this.
- All PRs merge into `master` using **Squash and merge** (so the PR title becomes the one commit message release-please parses). This is a GitHub repo setting the user must set manually (see Task 16) — code changes in this plan cannot set it.
- Ruff line-length 120, `select = ["E","W","F","I"]` (unchanged) — keep all new code passing `ruff check .` and `ruff format`.
- PyPI publishing uses **Trusted Publishing (OIDC)** — no PyPI API token is ever stored as a GitHub secret.
- Every task that touches Python code ends with `pytest -m "not live"` passing locally before commit; live-marked tests hit real network and are allowed to be validated less frequently (see Task 4).
- v1.0.0 ships through a **release-candidate channel first** (`1.0.0-rc.1`, `1.0.0-rc.2`, ... → normalizes to PEP 440 `1.0.0rc1`, `1.0.0rc2` on PyPI, verified locally with `packaging.version.Version`). RCs are real PyPI prereleases (`pip install --pre` or an exact pin only — never installed by a plain `pip install bible-translations`), so they're safe to publish and iterate on before committing to the final version.
- **The final graduation from release-candidate to stable `v1.0.0` is performed only by the repo owner, never by an agent.** Fable (or any executor) may prepare, and even merge, intermediate RC release-please PRs while iterating, but must stop at Task 17 and hand the graduation steps to the user. This is a hard boundary, not a preference — do not merge the graduation release-please PR under any circumstance while executing this plan autonomously.
- Before starting Task 1, the executor must complete **Task 0** (a critical read-through of this whole plan against the live repo) and get explicit user sign-off. Do not begin Task 1 until that sign-off is given.

---

## File Structure

New or modified files this plan touches, grouped by responsibility:

```
pyproject.toml                                  # requires-python, docs/dev deps, pytest markers
CHANGELOG.md                                    # trimmed to a header; release-please owns the rest
README.md                                       # repositioned as fetch-on-demand tool, docs link, ASV added
CONTRIBUTING.md                                 # master (not main), Conventional Commits, squash-merge

release-please-config.json                      # NEW - release-please package config
.release-please-manifest.json                   # NEW - release-please version tracking

.github/workflows/ci.yml                        # matrix bump, split unit/live test jobs
.github/workflows/lint.yml                       # branch trigger cleanup only
.github/workflows/pr-title-lint.yml             # NEW - Conventional Commit PR title enforcement
.github/workflows/cd.yml                        # NEW - release-please + PyPI trusted publish
.github/workflows/docs.yml                      # NEW - mkdocs build + GitHub Pages deploy

mkdocs.yml                                       # NEW - docs site config
docs/index.md                                    # NEW - docs home
docs/cli.md                                      # NEW - auto-generated CLI reference
docs/api.md                                      # NEW - auto-generated API reference
docs/changelog.md                                # NEW - embeds CHANGELOG.md

scripts/capture_fixtures.py                      # NEW - one-off script to (re)capture HTML fixtures
tests/fixtures/bible_gateway/kjv_john_3.html      # NEW - captured fixture
tests/fixtures/bible_gateway/kjv_john_3_16.html   # NEW - captured fixture

src/bible_translations/__init__.py               # public API surface (currently empty)
src/bible_translations/constants.py              # VERSION becomes computed, not hardcoded
src/bible_translations/translations/asv.py       # NEW - ASV translation
src/bible_translations/translations/__init__.py  # register ASV
src/bible_translations/utils/flatten.py          # NEW - FlatVerse + flatten_books()
src/bible_translations/utils/exporter.py         # flat export support, DRY info-json helper
src/bible_translations/cli.py                    # --flat flag on all 5 commands

tests/test_kjv.py                                # mark existing tests @pytest.mark.live
tests/test_asv.py                                # NEW - ASV live smoke tests
tests/test_bible_gateway_unit.py                 # NEW - offline fixture-based parsing tests
tests/test_flatten.py                            # NEW - flatten_books unit tests
tests/test_exports.py                            # + flat export test
tests/test_cli.py                                # + --flat flag presence checks
tests/test_public_api.py                         # NEW - public API surface contract test
```

---

## Task 0: Review this plan before starting execution

This plan was written from a snapshot of the repo taken during planning. Before touching anything, the executor (Fable) must critically re-read the whole plan against the live repo, and surface — not silently fix — anything that's drifted or missing, so the user can weigh in before real work starts.

**Files:** none (read-only review)

- [ ] **Step 1: Re-verify the starting state assumptions**

```bash
git status
git log --oneline -5
git branch -a
pytest -q
```

Confirm: `development` and `master` are in the state this plan assumes (see Task 1), the test count still matches what's referenced throughout (23 passed), and nothing has been hand-edited since planning that would make a task's "Files" or code snippets stale (e.g. if `cli.py`, `exporter.py`, `base.py`, or `bible_gateway.py` have changed, re-diff this plan's snippets against the current file contents before trusting them verbatim).

- [ ] **Step 2: Re-verify the external assumptions this plan depends on**

- BibleGateway's markup for KJV and ASV still matches what's described in Tasks 5–6 (container class `div.version-{ABBR}.result-text-style-normal.text-html`, verse span class `{Book}-{chapter}-{verse}`) — spot-check with a live request if in doubt.
- The `bible-translations` PyPI project name is still unclaimed (re-check `https://pypi.org/pypi/bible-translations/json` returns 404) before relying on Trusted Publisher "pending publisher" registration in Task 15.
- GitHub issues #22 (flatten) and #4 (paragraph breaks) haven't been closed/resolved by someone else in the meantime in a way that changes this plan's scope.

- [ ] **Step 3: Check for gaps**

Read every task's Global Constraints coverage, file list, and step sequence end-to-end and identify anything that seems missing, redundant, wrongly ordered, or under-specified given the current state of the repo. This includes, but isn't limited to: dependency versions that may have moved on, new GitHub Actions action versions (`actions/checkout@v5`, `actions/setup-python@v6`, `googleapis/release-please-action@v4`, `pypa/gh-action-pypi-publish@release/v1`, `amannn/action-semantic-pull-request@v5`) that may have newer major versions worth pinning to instead, and any interaction between tasks that wasn't obvious when they were written independently.

- [ ] **Step 4: Report back before proceeding**

Summarize, for the user: (a) anything found in Steps 1–2 that contradicts this plan's assumptions, (b) any gaps or additions found in Step 3, with a concrete proposed fix for each, and (c) explicit confirmation that Task 17 (final stable release graduation) will be left for the user to perform. **Do not start Task 1 until the user has responded to this summary.**

No commit for this task — it produces a review, not a code change.

---

## Task 1: Consolidate git history onto `master`

`development` currently contains the entire rewritten package (everything under `src/`); `master` still holds the old pre-rewrite repo. Local branches `20-cli` and `24-ci` are already fully merged into `development`. Several `origin/*` branches exist for already-closed issues and need verification before deletion.

**Files:**
- Modify: `.github/workflows/lint.yml` (drop the retired `development` branch from its trigger — Step 9)

- [ ] **Step 1: Confirm `development` is clean and up to date**

```bash
git checkout development
git status
git pull origin development
```

Expected: "nothing to commit, working tree clean" and "Already up to date."

- [ ] **Step 2: Merge `development` into `master`**

```bash
git checkout master
git pull origin master
git merge --no-ff development -m "chore: merge development into master ahead of v1.0.0"
```

- [ ] **Step 3: Run the full test suite on the merged `master` to confirm nothing was lost in the merge**

```bash
pip install -e ".[dev]"
pytest -q
```

Expected: 23 passed (same as on `development` before the merge).

- [ ] **Step 4: Push `master`**

```bash
git push origin master
```

- [ ] **Step 5: Confirm GitHub's default branch is already `master`**

```bash
git remote show origin | grep "HEAD branch"
```

Expected: `HEAD branch: master`. (It already is — no repo-settings change needed here.)

- [ ] **Step 6: Delete the now-redundant `development` branch, locally and on `origin`**

```bash
git branch -d development
git push origin --delete development
```

- [ ] **Step 7: Delete local feature branches already merged into `development`/`master`**

```bash
git branch -d 20-cli 24-ci
```

- [ ] **Step 8: Verify which stale `origin/*` branches are fully merged into `master`, and delete only those**

```bash
git fetch --prune
for b in 13-clear-branch 15-linter 17-python-structure 19-first-translation 20-cli 21-exporter 24-ci jadenzaleski-patch-1; do
  if git merge-base --is-ancestor "origin/$b" origin/master 2>/dev/null; then
    echo "MERGED (safe to delete): $b"
  else
    echo "NOT MERGED (leave alone): $b"
  fi
done
```

Delete only the branches printed as "MERGED":

```bash
git push origin --delete <each-merged-branch-name>
```

Do not delete any branch printed as "NOT MERGED" without checking with the repo owner first — it may hold work that never made it into `development`.

- [ ] **Step 9: Drop the retired `development` branch from `lint.yml`'s trigger**

`.github/workflows/lint.yml` still triggers on `push: branches: [master, development]`. Since `development` no longer exists after Step 6, change it to:

```yaml
on:
  workflow_dispatch:
  push:
    branches: [master, development]
  pull_request:
```

becomes:

```yaml
on:
  workflow_dispatch:
  push:
    branches: [master]
  pull_request:
```

```bash
git add .github/workflows/lint.yml
git commit -m "ci: drop retired development branch from lint workflow trigger"
git push origin master
```

This is the one small commit this task does make, on top of the merge commit from Step 4.

---

## Task 2: Broaden Python compatibility and expand the CI matrix

The package currently requires Python ≥3.14 (released only months ago), which will block almost every PyPI installer at launch. Nothing in the current codebase uses 3.14-only syntax (dataclasses, `X | None` unions, and f-strings are all fine back to 3.10+), so lower the floor and verify across a real matrix.

**Files:**
- Modify: `pyproject.toml`
- Modify: `.github/workflows/ci.yml`

- [ ] **Step 1: Lower the Python floor in `pyproject.toml`**

Change:
```toml
requires-python = ">=3.14"
```
to:
```toml
requires-python = ">=3.11"
```

Also remove the now-stale duplication comment on the same block (this is fixed properly in Task 3):
```toml
version = "0.1.0" # MUST ALSO CHANGE IN constants.py
```
stays as-is for this task — Task 3 removes the comment when it removes the duplication.

- [ ] **Step 1b: Fix the trove classifiers to match reality**

PyPA convention is one `Programming Language :: Python :: 3.X` classifier per *actually supported* minor version, and a `Development Status` classifier that reflects real project maturity — not left on whatever it was set to at scaffolding time. Change:

```toml
classifiers = [
    "Development Status :: 2 - Pre-Alpha",
    "Intended Audience :: Developers",
    "Topic :: Religion",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3.14",
]
```

to:

```toml
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Topic :: Religion",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
]
```

`4 - Beta` is correct for the whole RC-channel period (Task 16). Task 17 bumps this one more time, to `5 - Production/Stable`, as part of graduating to the real `1.0.0`.

- [ ] **Step 2: Expand the CI matrix in `.github/workflows/ci.yml`**

Change:
```yaml
    strategy:
      matrix:
        python-version: ["3.14"]
```
to:
```yaml
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13", "3.14"]
```

- [ ] **Step 3: Run the suite locally on whatever interpreter is available to sanity-check nothing regresses**

```bash
pip install -e ".[dev]"
pytest -q
```

Expected: 23 passed. (Cross-version verification itself happens in CI once pushed — that's the point of the matrix.)

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml .github/workflows/ci.yml
git commit -m "build: lower minimum supported Python to 3.11, expand CI matrix, and update trove classifiers"
```

---

## Task 3: Single-source the package version

`VERSION` is currently hardcoded in `src/bible_translations/constants.py` **and** duplicated in `pyproject.toml`, synced only by a comment reminder. This is exactly the kind of manual step that breaks under an automated release pipeline (release-please only bumps `pyproject.toml`). Make `pyproject.toml`'s `[project].version` the sole source of truth, and read it at runtime via `importlib.metadata`.

**Files:**
- Modify: `src/bible_translations/constants.py`
- Modify: `pyproject.toml`

**Interfaces:**
- Produces: `bible_translations.constants.VERSION: str` — same name and type as before, so no downstream code (`cli.py`, tests) needs to change.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_cli.py` (it already asserts `VERSION in result.output`, which is the right test — first confirm the *current* hardcoded value still passes before changing the source):

```bash
pytest tests/test_cli.py::test_bt -q
```

Expected: PASS (using the still-hardcoded `VERSION = "0.1.0"`). This step is a checkpoint, not a new test file.

- [ ] **Step 2: Replace the hardcoded VERSION in `constants.py`**

Change:
```python
VERSION = "0.1.0"  # MUST ALSO CHANGE IN pyproject.toml
```
to:
```python
from importlib.metadata import PackageNotFoundError, version

try:
    VERSION = version("bible-translations")
except PackageNotFoundError:
    # Package isn't installed (e.g. running from a raw source checkout) — fall back.
    VERSION = "0.0.0-dev"
```

- [ ] **Step 3: Remove the now-stale duplication comment from `pyproject.toml`**

Change:
```toml
version = "0.1.0" # MUST ALSO CHANGE IN constants.py
```
to:
```toml
version = "0.1.0"
```

- [ ] **Step 4: Reinstall so package metadata reflects the current `pyproject.toml`, then re-run the test**

```bash
pip install -e ".[dev]"
pytest tests/test_cli.py::test_bt -q
```

Expected: PASS — `VERSION` now resolves to `"0.1.0"` via `importlib.metadata` instead of the hardcoded string, and the CLI's `--version` output still contains it (`click.version_option(version=VERSION)` in `cli.py` is unaffected — it just consumes whatever `VERSION` resolves to).

- [ ] **Step 5: Run the full suite**

```bash
pytest -q
```

Expected: 23 passed.

- [ ] **Step 6: Commit**

```bash
git add src/bible_translations/constants.py pyproject.toml
git commit -m "build: derive VERSION from installed package metadata instead of a hardcoded duplicate"
```

---

## Task 4: Tag and stabilize the network-dependent test suite

`tests/test_kjv.py` and `tests/test_exports.py::test_export_single_verse` currently make real, unmocked HTTP requests to BibleGateway on every test run (23 tests, ~59s locally). Under an automated release pipeline, a transient network blip or BibleGateway hiccup would block a release. Mark these tests explicitly as `live`, add automatic retries for transient failures, and split CI into a fast "always run" unit job and a slower "live" job.

**Files:**
- Modify: `pyproject.toml`
- Modify: `tests/test_kjv.py`
- Modify: `tests/test_exports.py`
- Modify: `.github/workflows/ci.yml`

- [ ] **Step 1: Register the `live` marker and add `pytest-rerunfailures`**

In `pyproject.toml`, add the marker registration to the existing `[tool.pytest.ini_options]` block:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
markers = [
    "live: exercises the real network (BibleGateway) — slower and can be flaky.",
]
```

Add `pytest-rerunfailures` to the dev dependency group:

```toml
[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-asyncio",
    "pytest-rerunfailures",
    "ruff",
    "build"
]
```

- [ ] **Step 2: Mark every test in `tests/test_kjv.py` as `live`**

Add `import pytest` (already imported) and prefix every test function with `@pytest.mark.live`, in addition to the existing `@pytest.mark.asyncio`. Example for the first test (repeat the same pattern for all 14 tests in the file):

```python
@pytest.mark.live
@pytest.mark.asyncio
async def test_aget_verse_john_3_16():
    kjv = KJV()
    verse = await kjv.aget_verse(book_name="John", chapter_number=3, verse_number=16)
    ...
```

Apply `@pytest.mark.live` to: `test_aget_verse_john_3_16`, `test_aget_verse_amos_9_8`, `test_aget_verse_invalid_book`, `test_aget_verse_invalid_chapter`, `test_aget_verse_invalid_verse`, `test_aget_chapter_john_1`, `test_aget_chapter_invalid_chapter`, `test_aget_chapter_invalid_book`, `test_aget_book_john`, `test_aget_book_invalid_book`, `test_aget_books`, `test_aget_selection_matthew`, `test_aget_selection_mode_ref`, `test_aget_selection_mode_ref_multi_book`, `test_aget_selection_invalid_mode_ref`, `test_aget_selection_invalid`.

- [ ] **Step 3: Mark the network-dependent export test as `live`**

In `tests/test_exports.py`, add `import pytest` and mark `test_export_single_verse`:

```python
@pytest.mark.live
@pytest.mark.asyncio
async def test_export_single_verse(tmp_path):
    ...
```

- [ ] **Step 4: Verify the fast (non-live) suite runs and is now empty until later tasks add unit tests**

```bash
pip install -e ".[dev]"
pytest -m "not live" -q
```

Expected: `6 passed` (all six `test_cli.py` tests — none of them touch the network). Fixture-based unit tests added in Task 5 will grow this set.

- [ ] **Step 5: Verify the live suite still passes**

```bash
pytest -m live -q
```

Expected: `17 passed` (16 from `test_kjv.py` + 1 from `test_exports.py`).

- [ ] **Step 6: Split `.github/workflows/ci.yml` into a fast `unit-tests` job (full matrix) and a `live-tests` job (single Python version, with reruns)**

Replace the entire `test` job with:

```yaml
name: CI
on:
  workflow_dispatch:
  push:
    branches: [ "master" ]
  pull_request:
    branches: [ "master" ]
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13", "3.14"]
    steps:
      - uses: actions/checkout@v5
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"
      - name: Run unit tests (no network)
        run: pytest -m "not live"

  live-tests:
    needs: unit-tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: "3.14"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"
      - name: Run live tests (real network, retried on transient failure)
        run: pytest -m live --reruns 3 --reruns-delay 5
```

Running `live-tests` only once (not across the full matrix) avoids hammering BibleGateway four times per PR.

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml tests/test_kjv.py tests/test_exports.py .github/workflows/ci.yml
git commit -m "test: mark network-dependent tests as live, split CI into unit and live jobs"
```

---

## Task 5: Add offline fixture-based unit tests for BibleGateway parsing

Task 4 quarantined the network tests but left zero fast coverage of the actual HTML-parsing logic in `BibleGatewayTranslation.aget_chapter` / `aget_verse`. Capture real BibleGateway HTML once, commit it as a fixture, and test the parsing logic against it with the network mocked out.

**Files:**
- Create: `scripts/capture_fixtures.py`
- Create: `tests/fixtures/bible_gateway/kjv_john_3.html` (generated by the script)
- Create: `tests/fixtures/bible_gateway/kjv_john_3_16.html` (generated by the script)
- Create: `tests/test_bible_gateway_unit.py`

**Interfaces:**
- Consumes: `bible_translations.utils.fetch.bible_gateway.BibleGatewayClient.fetch(query: str) -> BeautifulSoup` (existing).
- Consumes: `bible_translations.translations.kjv.KJV` (existing), specifically `aget_chapter(book_name, chapter_number)` and `aget_verse(book_name, chapter_number, verse_number)`.

- [ ] **Step 1: Write the fixture-capture script**

```python
"""One-off script to (re)capture real BibleGateway HTML for offline unit tests.

Run manually whenever BibleGateway's markup changes and fixtures need refreshing:
    python scripts/capture_fixtures.py
"""

import asyncio
from pathlib import Path

from bible_translations.utils.fetch.bible_gateway import BibleGatewayClient

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "bible_gateway"

QUERIES = {
    "kjv_john_3.html": "John+3&version=KJV",
    "kjv_john_3_16.html": "John+3:16&version=KJV",
}


async def main():
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    async with BibleGatewayClient() as client:
        for filename, query in QUERIES.items():
            soup = await client.fetch(query)
            (FIXTURES_DIR / filename).write_text(str(soup), encoding="utf-8")
            print(f"Wrote {filename}")


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 2: Run the script to generate the fixtures (requires network, one-time)**

```bash
mkdir -p tests/fixtures/bible_gateway
python scripts/capture_fixtures.py
```

Expected output:
```
Wrote kjv_john_3.html
Wrote kjv_john_3_16.html
```

- [ ] **Step 3: Write the failing tests**

```python
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from bs4 import BeautifulSoup

from bible_translations.translations.kjv import KJV

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "bible_gateway"


def _load_fixture(name: str) -> BeautifulSoup:
    html = (FIXTURES_DIR / name).read_text(encoding="utf-8")
    return BeautifulSoup(html, "html.parser")


@pytest.mark.asyncio
async def test_aget_chapter_parses_fixture_without_network():
    kjv = KJV()
    fixture_soup = _load_fixture("kjv_john_3.html")
    with patch(
        "bible_translations.utils.fetch.bible_gateway.BibleGatewayClient.fetch",
        new=AsyncMock(return_value=fixture_soup),
    ):
        chapter = await kjv.aget_chapter("John", 3)
    assert chapter.number == 3
    assert len(chapter.verses) == 36
    assert chapter.verses[15].number == 16
    assert chapter.verses[15].text.startswith("For God so loved the world")


@pytest.mark.asyncio
async def test_aget_verse_parses_fixture_without_network():
    kjv = KJV()
    fixture_soup = _load_fixture("kjv_john_3_16.html")
    with patch(
        "bible_translations.utils.fetch.bible_gateway.BibleGatewayClient.fetch",
        new=AsyncMock(return_value=fixture_soup),
    ):
        verse = await kjv.aget_verse("John", 3, 16)
    assert verse.number == 16
    assert verse.text == (
        "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not"
        " perish, but have everlasting life."
    )
```

Save as `tests/test_bible_gateway_unit.py`.

- [ ] **Step 4: Run the tests to verify they pass against the captured fixtures**

```bash
pytest tests/test_bible_gateway_unit.py -v
```

Expected: `2 passed`. (These do not need a "verify it fails first" step in the usual TDD sense — the fixture files must exist before the test can even be written meaningfully, so Steps 1–2 already established the precondition. If chapter 3 verse counts differ from what's asserted, open the fixture file and adjust the assertions to match reality — do not adjust the scraper.)

- [ ] **Step 5: Confirm these count toward the fast suite**

```bash
pytest -m "not live" -q
```

Expected: `8 passed` (6 from `test_cli.py` + 2 new).

- [ ] **Step 6: Commit**

```bash
git add scripts/capture_fixtures.py tests/fixtures/bible_gateway tests/test_bible_gateway_unit.py
git commit -m "test: add offline fixture-based unit tests for BibleGateway parsing"
```

---

## Task 6: Add the ASV translation

Confirmed live against BibleGateway during planning: `https://www.biblegateway.com/passage/?search=John+3:16&version=ASV` returns a container with class `version-ASV` and a verse span with class `John-3-16` — identical structure to KJV. `BibleGatewayTranslation`'s default `_get_container_selector()` (`div.version-{abbreviation}.result-text-style-normal.text-html`) needs no override; ASV is a pure metadata subclass, same as `KJV`.

**Files:**
- Create: `src/bible_translations/translations/asv.py`
- Modify: `src/bible_translations/translations/__init__.py`
- Create: `tests/test_asv.py`
- Modify: `README.md` (translations table)

**Interfaces:**
- Produces: `bible_translations.translations.asv.ASV` (class), registered in `TRANSLATIONS["ASV"]`.

- [ ] **Step 1: Write the failing test**

```python
import pytest

from bible_translations.translations.asv import ASV


@pytest.mark.live
@pytest.mark.asyncio
async def test_aget_verse_john_3_16():
    asv = ASV()
    verse = await asv.aget_verse(book_name="John", chapter_number=3, verse_number=16)
    # https://www.biblegateway.com/passage/?search=John%203%3A16&version=ASV
    assert verse.number == 16
    assert "For God so loved the world" in verse.text


@pytest.mark.live
@pytest.mark.asyncio
async def test_aget_chapter_john_3():
    asv = ASV()
    chapter = await asv.aget_chapter(book_name="John", chapter_number=3)
    assert chapter.number == 3
    assert chapter.verses[15].number == 16


@pytest.mark.live
@pytest.mark.asyncio
async def test_aget_book_john():
    asv = ASV()
    book = await asv.aget_book(name="John")
    assert len(book.chapters) == 21
    assert book.chapters[0].verses[0].number == 1
```

Save as `tests/test_asv.py`.

- [ ] **Step 2: Run it to verify it fails (no `ASV` class exists yet)**

```bash
pytest tests/test_asv.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'bible_translations.translations.asv'`.

- [ ] **Step 3: Implement the ASV translation class**

```python
from bible_translations.translations.bible_gateway import BibleGatewayTranslation


class ASV(BibleGatewayTranslation):
    """
    American Standard Version (1901) backed by BibleGateway scraping.

    Inherits all retrieval methods from BibleGatewayTranslation so that the
    scraping logic is shared across translations.
    """

    name = "American Standard Version"
    abbreviation = "ASV"
    copyright = "Public Domain"
    url = "https://www.biblegateway.com"
```

Save as `src/bible_translations/translations/asv.py`.

- [ ] **Step 4: Register ASV in the translation registry**

Change `src/bible_translations/translations/__init__.py`:

```python
from .asv import ASV
from .kjv import KJV

TRANSLATIONS = {
    "KJV": KJV,
    "ASV": ASV,
}


def get_translation(abbreviation: str):
    """
    Get a translation class by its abbreviation.

    :param abbreviation: The translation abbreviation (e.g., "KJV").
    :return: The translation class.
    :raises ValueError: If the translation is not found.
    """
    translation_class = TRANSLATIONS.get(abbreviation.upper())
    if not translation_class:
        raise ValueError(
            f"Translation not found: {abbreviation}. Available translations: {', '.join(TRANSLATIONS.keys())}"
        )
    return translation_class()
```

- [ ] **Step 5: Run the ASV tests to verify they pass**

```bash
pytest tests/test_asv.py -v
```

Expected: `3 passed`.

- [ ] **Step 6: Run the full suite**

```bash
pytest -q
```

Expected: all previously-passing tests still pass, plus the 3 new ASV tests (all `live`).

- [ ] **Step 7: Update the README translations table**

In `README.md`, replace the placeholder table (this table is fully reworked again in Task 10 to drop the SQL/JSON download columns — for now just add the ASV row):

```markdown
| Translation | Abbreviation | Copyright     |
|-------------|--------------|---------------|
| KJV         | KJV          | Public Domain |
| ASV         | ASV          | Public Domain |
```

- [ ] **Step 8: Commit**

```bash
git add src/bible_translations/translations/asv.py src/bible_translations/translations/__init__.py tests/test_asv.py README.md
git commit -m "feat: add ASV (American Standard Version) translation"
```

---

## Task 7: Add the flatten API (`FlatVerse` + `flatten_books`)

Implements GitHub issue #22: flatten the nested `Book → Chapter → Verse` structure into a flat list of per-verse records, useful for export and downstream processing (CSV, dataframes, DB rows).

**Files:**
- Create: `src/bible_translations/utils/flatten.py`
- Create: `tests/test_flatten.py`

**Interfaces:**
- Produces: `FlatVerse` (dataclass: `translation: str`, `abbreviation: str`, `book: str`, `chapter: int`, `verse: int`, `text: str`, `heading: str | None`, `superscription: str | None`, `footnotes: list[str] | None`).
- Produces: `flatten_books(books: list[Book]) -> list[FlatVerse]`.
- Consumes: `bible_translations.models.book.Book`, `.chapter.Chapter`, `.verse.Verse`, `.info.Info` (all existing, unchanged).

- [ ] **Step 1: Write the failing tests**

```python
from bible_translations.models.book import Book
from bible_translations.models.chapter import Chapter
from bible_translations.models.info import Info
from bible_translations.models.verse import Verse
from bible_translations.utils.flatten import FlatVerse, flatten_books


def _make_book() -> Book:
    info = Info(translation="King James Version", abbreviation="KJV", language="English", copyright="Public Domain")
    verses_ch1 = [Verse(number=1, text="In the beginning..."), Verse(number=2, text="And the earth was...")]
    verses_ch2 = [Verse(number=1, text="Thus the heavens...")]
    return Book(
        name="Genesis",
        chapters=[Chapter(number=1, verses=verses_ch1), Chapter(number=2, verses=verses_ch2)],
        info=info,
    )


def test_flatten_books_produces_one_record_per_verse():
    flat = flatten_books([_make_book()])
    assert len(flat) == 3
    assert all(isinstance(r, FlatVerse) for r in flat)


def test_flatten_books_preserves_reference_and_text():
    flat = flatten_books([_make_book()])
    first = flat[0]
    assert first.translation == "King James Version"
    assert first.abbreviation == "KJV"
    assert first.book == "Genesis"
    assert first.chapter == 1
    assert first.verse == 1
    assert first.text == "In the beginning..."


def test_flatten_books_handles_missing_info():
    book = Book(name="Genesis", chapters=[Chapter(number=1, verses=[Verse(number=1, text="x")])], info=None)
    flat = flatten_books([book])
    assert flat[0].translation == ""
    assert flat[0].abbreviation == ""
```

Save as `tests/test_flatten.py`.

- [ ] **Step 2: Run to verify it fails**

```bash
pytest tests/test_flatten.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'bible_translations.utils.flatten'`.

- [ ] **Step 3: Implement `flatten.py`**

```python
from dataclasses import dataclass

from bible_translations.models.book import Book


@dataclass
class FlatVerse:
    """A single verse flattened out of the nested Book/Chapter/Verse structure."""

    translation: str
    abbreviation: str
    book: str
    chapter: int
    verse: int
    text: str
    heading: str | None = None
    superscription: str | None = None
    footnotes: list[str] | None = None


def flatten_books(books: list[Book]) -> list[FlatVerse]:
    """
    Flatten a list of Book objects into a flat list of per-verse records.

    :param books: List of Book objects to flatten.
    :returns: list[FlatVerse]: One record per verse, in book/chapter/verse order.
    """
    flat: list[FlatVerse] = []
    for book in books:
        info = book.info
        translation = info.translation if info else ""
        abbreviation = info.abbreviation if info else ""
        for chapter in book.chapters:
            for verse in chapter.verses:
                flat.append(
                    FlatVerse(
                        translation=translation,
                        abbreviation=abbreviation,
                        book=book.name,
                        chapter=chapter.number,
                        verse=verse.number,
                        text=verse.text,
                        heading=verse.heading,
                        superscription=verse.superscription,
                        footnotes=verse.footnotes,
                    )
                )
    return flat
```

Save as `src/bible_translations/utils/flatten.py`.

- [ ] **Step 4: Run the tests to verify they pass**

```bash
pytest tests/test_flatten.py -v
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

```bash
git add src/bible_translations/utils/flatten.py tests/test_flatten.py
git commit -m "feat: add flatten_books/FlatVerse for flattening nested translation results (#22)"
```

---

## Task 8: Wire flatten into the Exporter and CLI (`--flat`)

Expose Task 7's `flatten_books` through both the exporter (a `_flat.json` export) and the CLI (a `--flat` flag on all five commands).

**Files:**
- Modify: `src/bible_translations/utils/exporter.py`
- Modify: `src/bible_translations/cli.py`
- Modify: `tests/test_exports.py`
- Modify: `tests/test_cli.py`

**Interfaces:**
- Consumes: `flatten_books` from Task 7.
- Produces: `Exporter.export(..., flat: bool = False)` (new parameter, default preserves current behavior).
- Produces: `--flat` CLI flag on `verse`, `chapter`, `book`, `books`, `selection`.

- [ ] **Step 1: Write the failing exporter test**

Add to `tests/test_exports.py` (add `import json` and import `Info`, `Verse` at the top alongside the existing imports):

```python
import json
import logging
import zipfile

import pytest

from bible_translations.models.book import Book
from bible_translations.models.chapter import Chapter
from bible_translations.models.info import Info
from bible_translations.models.verse import Verse
from bible_translations.translations.kjv import KJV
from bible_translations.utils.exporter import Exporter


def test_export_flat_json(tmp_path):
    info = Info(translation="King James Version", abbreviation="KJV", language="English", copyright="Public Domain")
    book = Book(
        name="John",
        chapters=[Chapter(number=3, verses=[Verse(number=16, text="For God so loved...")])],
        info=info,
    )
    exporter = Exporter(output_dir=tmp_path)

    zip_path = exporter.export([book], flat=True)

    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
        assert "kjv_flat.json" in names
        assert "kjv_info.json" in names
        with z.open("kjv_flat.json") as f:
            data = json.load(f)
        assert data == [
            {
                "translation": "King James Version",
                "abbreviation": "KJV",
                "book": "John",
                "chapter": 3,
                "verse": 16,
                "text": "For God so loved...",
                "heading": None,
                "superscription": None,
                "footnotes": None,
            }
        ]
```

(Leave the existing `test_export_single_verse` test in place, unchanged, still marked `@pytest.mark.live` from Task 4.)

- [ ] **Step 2: Run it to verify it fails**

```bash
pytest tests/test_exports.py::test_export_flat_json -v
```

Expected: FAIL with `TypeError: Exporter.export() got an unexpected keyword argument 'flat'`.

- [ ] **Step 3: Refactor the info-JSON write into a shared helper, then add `_export_json_flat`**

In `src/bible_translations/utils/exporter.py`, add the import:

```python
from dataclasses import asdict
```

and

```python
from bible_translations.utils.flatten import flatten_books
```

Change the `export` method signature and dispatch:

```python
    def export(
        self,
        books: List[Book],
        file_format: str = "json",
        compression: Literal[".tar.gz", ".tgz", ".zip"] = ".zip",
        folder_name: str | None = None,
        flat: bool = False,
    ) -> Path:
        """
        Export books to the specified format.

        :param folder_name: Name of the exported folder
        :param compression: Type of compression to use (tar.gz, tgz, zip)
        :param books: List of Book objects to export
        :param file_format: Export format (json, txt, csv, xml)
        :param flat: If True, export a single flat list of verse records instead of the
            nested book/chapter/verse structure.
        :return: Path to the exported file
        """
```

(only the signature and docstring change; the temp-directory/assembly-folder logic above the format dispatch is unchanged)

Change the format dispatch block:

```python
            if file_format == "json":
                if flat:
                    self._export_json_flat(books, parent_folder, book_info)
                else:
                    self._export_json(books, parent_folder, book_info)
            elif file_format == "sql":
                raise NotImplementedError("SQL export not implemented yet")
            else:
                raise ValueError(f"Unsupported file format: {file_format}")
```

Extract the info-writing block out of `_export_json` into a shared static helper:

```python
    @staticmethod
    def _write_info_json(output_dir: str, info: Info) -> dict:
        info_data = {
            "translation": info.translation or "",
            "abbreviation": info.abbreviation or "",
            "language": info.language or "",
            "copyright": info.copyright or "",
            "url": info.url or "",
            "fetch_date": info.fetch_date or "",
        }
        with open(output_dir + "/" + info.abbreviation.lower() + "_info.json", "w") as json_file:
            json.dump(info_data, json_file, indent=4)
        return info_data
```

Update `_export_json` to call it instead of inlining the info block:

```python
    @staticmethod
    def _export_json(books: List[Book], output_dir: str, info: Info):
        logger.debug("Exporting JSON files...")
        info_data = Exporter._write_info_json(output_dir, info)

        # Export each book as a separate JSON file
        for book in books:
            ...  # unchanged from here down
```

(everything from `for book in books:` through the end of the existing method body is unchanged — only the info-writing block at the top is replaced by the one-line call above)

Add the new flat export method:

```python
    @staticmethod
    def _export_json_flat(books: List[Book], output_dir: str, info: Info):
        logger.debug("Exporting flat JSON...")
        Exporter._write_info_json(output_dir, info)
        records = [asdict(record) for record in flatten_books(books)]
        file_path = Path(output_dir, info.abbreviation.lower() + "_flat.json")
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(records, json_file, indent=4, ensure_ascii=False)
        logger.debug("Flat JSON export completed for %d verse records", len(records))
```

- [ ] **Step 4: Run the exporter tests to verify they pass**

```bash
pytest tests/test_exports.py -m "not live" -v
```

Expected: `test_export_flat_json PASSED` (the other test in this file, `test_export_single_verse`, is `live` and skipped here).

- [ ] **Step 5: Wire `--flat` into the CLI**

In `src/bible_translations/cli.py`, update the shared export helper:

```python
def run_export(book_list, output_file, file_format, flat=False):
    exporter = Exporter()
    return exporter.export(book_list, file_format=file_format, folder_name=output_file, flat=flat)
```

For **each** of the five commands (`verse`, `chapter`, `book`, `books`, `selection`), add a `--flat` option and thread it through. Example for `verse` (apply the identical pattern to the other four):

```python
@cli.command()
@click.argument("reference", metavar="VERSE")
@click.option(
    "--output",
    "-o",
    "output_file",
    type=click.Path(writable=True),
    help="Output file path. Default is generated with date.",
)
@click.option(
    "--format",
    "-f",
    "file_format",
    default="json",
    type=click.Choice(SUPPORTED_FORMATS, case_sensitive=False),
    show_default=True,
    help="Output format.",
)
@click.option(
    "--translation",
    "-t",
    default="KJV",
    type=click.Choice(list(TRANSLATIONS.keys()), case_sensitive=False),
    show_default=True,
    help="Bible translation to use.",
)
@click.option(
    "--flat",
    is_flag=True,
    help="Export a flat list of verse records instead of the nested book/chapter/verse structure.",
)
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output.")
def verse(reference, output_file, file_format, translation, flat, verbose):
    """Fetch and export a specific verse (e.g., 'John 3:16')."""
    ...  # body unchanged except the run_export call below
            export_task = progress.add_task(description="Exporting...", total=1)
            output_path = run_export([book_obj], output_file, file_format, flat)
            progress.update(export_task, advance=1, description=f"Exported {book_name} {chapter_num}:{verse_num}")
```

Repeat: add the `--flat` option (identical block) and the `flat` parameter to `chapter`, `book`, `books`, `selection`, and update each of their `run_export(...)` call sites to pass `flat` as the fourth positional argument.

- [ ] **Step 6: Extend the CLI tests to assert the flag exists**

In `tests/test_cli.py`, add `assert "--flat" in result.output` to each of the five `--help` tests:

```python
def test_bt_verse():
    """Test that the CLI verse runs."""
    runner = CliRunner()
    result = runner.invoke(cli, ["verse", "--help"])  # type: ignore
    assert result.exit_code == 0
    assert "--flat" in result.output


def test_bt_chapter():
    """Test that the CLI chapter runs."""
    runner = CliRunner()
    result = runner.invoke(cli, ["chapter", "--help"])  # type: ignore
    assert result.exit_code == 0
    assert "--flat" in result.output


def test_bt_book():
    """Test that the CLI book runs."""
    runner = CliRunner()
    result = runner.invoke(cli, ["book", "--help"])  # type: ignore
    assert result.exit_code == 0
    assert "--flat" in result.output


def test_bt_books():
    """Test that the CLI books runs."""
    runner = CliRunner()
    result = runner.invoke(cli, ["books", "--help"])  # type: ignore
    assert result.exit_code == 0
    assert "--flat" in result.output


def test_bt_selection():
    """Test that the CLI selection runs."""
    runner = CliRunner()
    result = runner.invoke(cli, ["selection", "--help"])  # type: ignore
    assert result.exit_code == 0
    assert "--flat" in result.output
```

- [ ] **Step 7: Run the fast suite**

```bash
pytest -m "not live" -q
```

Expected: all pass, including the updated CLI tests and `test_export_flat_json`.

- [ ] **Step 8: Run `ruff check` and `ruff format`**

```bash
ruff check . --fix
ruff format
```

- [ ] **Step 9: Commit**

```bash
git add src/bible_translations/utils/exporter.py src/bible_translations/cli.py tests/test_exports.py tests/test_cli.py
git commit -m "feat: wire flatten API into Exporter and CLI as a --flat flag (#22)"
```

---

## Task 9: Define the stable public package API surface

`src/bible_translations/__init__.py` is currently empty — anyone using this as a library has to know internal module paths (`bible_translations.translations.kjv.KJV`, etc.). For a v1.0.0 the top-level `import bible_translations` surface is a semver-guaranteed contract; define it explicitly.

**Files:**
- Modify: `src/bible_translations/__init__.py`
- Create: `tests/test_public_api.py`

**Interfaces:**
- Produces: `bible_translations.__version__`, `.Book`, `.Chapter`, `.Info`, `.Verse`, `.Translation`, `.TRANSLATIONS`, `.get_translation`, `.Exporter`, `.FlatVerse`, `.flatten_books`, `.BookNotFoundError`, `.ChapterNotFoundError`, `.VerseNotFoundError`, `.SelectionInvalidError`.

- [ ] **Step 1: Write the failing test**

```python
import bible_translations as bt

EXPECTED_PUBLIC_NAMES = {
    "__version__",
    "Book",
    "BookNotFoundError",
    "Chapter",
    "ChapterNotFoundError",
    "Exporter",
    "FlatVerse",
    "Info",
    "SelectionInvalidError",
    "TRANSLATIONS",
    "Translation",
    "Verse",
    "VerseNotFoundError",
    "flatten_books",
    "get_translation",
}


def test_public_api_exports_expected_names():
    assert EXPECTED_PUBLIC_NAMES.issubset(set(dir(bt)))
    assert set(bt.__all__) == EXPECTED_PUBLIC_NAMES


def test_public_api_get_translation_returns_kjv_instance():
    kjv = bt.get_translation("KJV")
    assert kjv.abbreviation == "KJV"
    assert isinstance(kjv, bt.Translation)


def test_public_api_flatten_books_is_reachable():
    book = bt.Book(name="Genesis", chapters=[bt.Chapter(number=1, verses=[bt.Verse(number=1, text="x")])])
    flat = bt.flatten_books([book])
    assert len(flat) == 1
    assert isinstance(flat[0], bt.FlatVerse)
```

Save as `tests/test_public_api.py`.

- [ ] **Step 2: Run to verify it fails**

```bash
pytest tests/test_public_api.py -v
```

Expected: FAIL — `dir(bt)` won't contain most of these names yet (`__init__.py` is empty).

- [ ] **Step 3: Implement the public API surface**

```python
"""bible_translations: fetch and export Bible translations on demand.

This package does not bundle any Bible text. Translations are scraped from
BibleGateway at request time, via either the `bt` / `bible-translations` CLI
or this Python API.
"""

from bible_translations.constants import VERSION as __version__
from bible_translations.exceptions import (
    BookNotFoundError,
    ChapterNotFoundError,
    SelectionInvalidError,
    VerseNotFoundError,
)
from bible_translations.models.book import Book
from bible_translations.models.chapter import Chapter
from bible_translations.models.info import Info
from bible_translations.models.verse import Verse
from bible_translations.translations import TRANSLATIONS, get_translation
from bible_translations.translations.base import Translation
from bible_translations.utils.exporter import Exporter
from bible_translations.utils.flatten import FlatVerse, flatten_books

__all__ = [
    "__version__",
    "Book",
    "BookNotFoundError",
    "Chapter",
    "ChapterNotFoundError",
    "Exporter",
    "FlatVerse",
    "Info",
    "SelectionInvalidError",
    "TRANSLATIONS",
    "Translation",
    "Verse",
    "VerseNotFoundError",
    "flatten_books",
    "get_translation",
]
```

Save as `src/bible_translations/__init__.py`.

- [ ] **Step 4: Run the tests to verify they pass**

```bash
pytest tests/test_public_api.py -v
```

Expected: `3 passed`.

- [ ] **Step 5: Run the full fast suite (checking for import cycles or breakage elsewhere)**

```bash
pytest -m "not live" -q
```

Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add src/bible_translations/__init__.py tests/test_public_api.py
git commit -m "feat: define the stable public API surface in bible_translations/__init__.py"
```

---

## Task 10: Reposition README/CONTRIBUTING for a fetch-on-demand tool

Per the repo owner: this release ships **no bundled translations**, only the ability to fetch them via API/CLI. The current README's "Download" section (a table implying precompiled SQL/JSON bundles) is aspirational and inaccurate — remove it. Also fix `CONTRIBUTING.md`'s stale branch reference (`main` doesn't exist; it's `master`) and document the Conventional Commits + squash-merge requirement.

**Files:**
- Modify: `README.md`
- Modify: `CONTRIBUTING.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Rewrite the top of `README.md`**

Replace the intro and the entire "Download" section. Note: the Release/PyPI/Downloads badges below will render as shields.io "not found" placeholders until Task 14's `cd.yml` exists and Task 16/17 actually publish a GitHub Release and PyPI package — that's expected at this point in the plan and self-resolves once those land; the CI/Lint/License/repo-activity badges are already live from Tasks 1–4.

```markdown
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
```

(the "Install" heading and everything below it — Install, Usage, Options, Changelog, Contributing, Disclaimer — is unchanged, keep it exactly as-is)

- [ ] **Step 2: Fix the branch reference and add commit/merge conventions to `CONTRIBUTING.md`**

Replace:

```markdown
6. Push and open a Pull Request to `main`.
```

with:

```markdown
6. Push and open a Pull Request to `master`.
```

And replace the commit-style bullet list:

```markdown
5. Commit with the following conventional style:
   * `feat:` add feature  
   * `fix:` resolve bug  
   * `docs:` update documentation  
```

with the fuller list actually enforced by CI (Task 13 adds a PR-title check for this):

```markdown
5. Commit with [Conventional Commits](https://www.conventionalcommits.org/) style — this repo's
   releases are automated with release-please, which reads these prefixes to decide version bumps
   and changelog entries:
   * `feat:` a new feature (minor version bump)
   * `fix:` a bug fix (patch version bump)
   * `docs:` documentation only
   * `chore:` maintenance with no user-facing effect
   * `refactor:` code change that neither fixes a bug nor adds a feature
   * `test:` adding or fixing tests
   * `ci:` CI/CD configuration
   * `build:` build system or dependency changes
   * `perf:` a performance improvement
   * A `!` after the type (e.g. `feat!:`) or a `BREAKING CHANGE:` footer triggers a major version bump.
```

Also add a note about merge strategy right after the "Steps" list, before "Guidelines":

```markdown
PRs are merged with **Squash and merge** — your PR title becomes the commit message on `master`,
so it must itself follow Conventional Commits.
```

- [ ] **Step 3: Trim `CHANGELOG.md` down to just the header**

release-please owns everything below the header from here on, prepending a new dated section per release. Replace the entire file with:

```markdown
# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/).
```

- [ ] **Step 4: Verify nothing broke**

```bash
pytest -m "not live" -q
```

Expected: all pass (this task touches no Python code).

- [ ] **Step 5: Commit**

```bash
git add README.md CONTRIBUTING.md CHANGELOG.md
git commit -m "docs: reposition README as a fetch-on-demand tool, fix CONTRIBUTING branch ref, trim CHANGELOG for release-please"
```

---

## Task 11: Add the documentation site (mkdocs + mkdocstrings + mkdocs-click)

Auto-generates both the API reference (from docstrings, via mkdocstrings) and the CLI reference (from the actual Click command tree, via mkdocs-click) — so docs can't drift from the code they describe.

**Files:**
- Modify: `pyproject.toml` (new `docs` optional-dependency group)
- Create: `mkdocs.yml`
- Create: `docs/index.md`
- Create: `docs/cli.md`
- Create: `docs/api.md`
- Create: `docs/changelog.md`

- [ ] **Step 1: Add the `docs` dependency group**

In `pyproject.toml`:

```toml
[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-asyncio",
    "pytest-rerunfailures",
    "ruff",
    "build"
]
docs = [
    "mkdocs",
    "mkdocs-material",
    "mkdocstrings[python]",
    "mkdocs-click"
]
```

- [ ] **Step 2: Write `mkdocs.yml`**

```yaml
site_name: bible-translations
site_description: A Python package and CLI for fetching Bible translations on demand.
site_url: https://jadenzaleski.github.io/bible-translations/
repo_url: https://github.com/jadenzaleski/bible-translations

theme:
  name: material
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      toggle:
        icon: material/brightness-4
        name: Switch to light mode

nav:
  - Home: index.md
  - CLI Reference: cli.md
  - API Reference: api.md
  - Changelog: changelog.md

markdown_extensions:
  - admonition
  - pymdownx.superfences
  - pymdownx.snippets:
      check_paths: true
  - mkdocs-click

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          options:
            show_source: true
            docstring_style: sphinx
```

- [ ] **Step 3: Write `docs/index.md`**

````markdown
# bible-translations

A Python package and CLI for fetching Bible translations on demand.

`bible-translations` does not ship any pre-downloaded Bible text. It scrapes
publicly available, public-domain translations from
[BibleGateway](https://www.biblegateway.com) at request time, and gives you
the result as Python objects (via the API) or as exported JSON files (via
the CLI).

## Install

```bash
pip install bible-translations
```

## Quickstart

### CLI

```bash
bt verse "John 3:16"
```

### API

```python
from bible_translations import get_translation

kjv = get_translation("KJV")
verse = kjv.get_verse("John", 3, 16)
print(verse.text)
```

See the [CLI Reference](cli.md) and [API Reference](api.md) for full details.
````

- [ ] **Step 4: Write `docs/cli.md`**

```markdown
# CLI Reference

::: mkdocs-click
    :module: bible_translations.cli
    :command: cli
    :prog_name: bt
    :depth: 1
    :style: table
    :list_subcommands: True
```

- [ ] **Step 5: Write `docs/api.md`**

```markdown
# API Reference

## Translations

::: bible_translations.translations.base.Translation

::: bible_translations.translations.get_translation

## Models

::: bible_translations.models.book.Book

::: bible_translations.models.chapter.Chapter

::: bible_translations.models.verse.Verse

::: bible_translations.models.info.Info

## Flattening

::: bible_translations.utils.flatten.flatten_books

::: bible_translations.utils.flatten.FlatVerse

## Exporting

::: bible_translations.utils.exporter.Exporter

## Exceptions

::: bible_translations.exceptions.BookNotFoundError

::: bible_translations.exceptions.ChapterNotFoundError

::: bible_translations.exceptions.VerseNotFoundError

::: bible_translations.exceptions.SelectionInvalidError
```

- [ ] **Step 6: Write `docs/changelog.md`**

```markdown
# Changelog

--8<-- "CHANGELOG.md"
```

- [ ] **Step 7: Build the site locally to verify it renders without errors**

```bash
pip install -e ".[docs]"
mkdocs build --strict
```

Expected: build succeeds with no warnings/errors (`--strict` turns mkdocstrings cross-reference warnings into failures, catching typos in the `:::` identifiers above before they reach production).

- [ ] **Step 8: Commit**

```bash
git add pyproject.toml mkdocs.yml docs/
git commit -m "docs: add mkdocs site with auto-generated API and CLI reference"
```

---

## Task 12: Deploy the docs site to GitHub Pages via CI

**Files:**
- Create: `.github/workflows/docs.yml`

- [ ] **Step 1: Write the deploy workflow**

```yaml
name: Docs

on:
  push:
    branches: [master]
  workflow_dispatch:

permissions:
  contents: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-python@v6
        with:
          python-version: "3.14"
      - name: Install docs dependencies
        run: pip install -e ".[docs]"
      - name: Deploy docs to GitHub Pages
        run: mkdocs gh-deploy --force --clean
```

`mkdocs gh-deploy` builds the site and force-pushes it to a `gh-pages` branch using the checked-out repo's git config and the default `GITHUB_TOKEN` credentials that `actions/checkout` already wires into the local git remote — no extra secrets needed.

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/docs.yml
git commit -m "ci: deploy docs to GitHub Pages on every push to master"
```

- [ ] **Step 3 (manual, one-time, do this after the workflow first runs on `master`): enable GitHub Pages**

In the repo's GitHub Settings → Pages, set **Source: Deploy from a branch**, **Branch: `gh-pages` / `(root)`**. This can only be done once the `gh-pages` branch exists, which only happens after this workflow runs once on `master` — so push this commit, let the workflow run, then flip the setting. After that, `https://jadenzaleski.github.io/bible-translations/` (already referenced in `mkdocs.yml` and the README) goes live.

---

## Task 13: Enforce Conventional Commit PR titles

release-please's version bumps depend entirely on Conventional Commit prefixes existing in `master`'s history. Since PRs merge via squash (Task 10's `CONTRIBUTING.md` note, formalized as a real repo setting in Task 16), the PR title *is* that commit message — enforce its format at PR time so a malformed title can't silently break the next release's version bump.

**Files:**
- Create: `.github/workflows/pr-title-lint.yml`

- [ ] **Step 1: Write the workflow**

```yaml
name: PR Title Lint

on:
  pull_request:
    types: [opened, edited, synchronize, reopened]
    branches: [master]

permissions:
  pull-requests: read

jobs:
  lint-pr-title:
    runs-on: ubuntu-latest
    steps:
      - uses: amannn/action-semantic-pull-request@v5
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

This defaults to the standard Conventional Commit type list (`feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `ci`, `build`, `perf`, `style`, `revert`) and fails the check if the PR title doesn't match `type(scope?): subject`.

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/pr-title-lint.yml
git commit -m "ci: enforce Conventional Commit PR titles"
```

---

## Task 14: Add release-please + PyPI trusted-publishing CD, with a release-candidate channel

The core of "fully automated release": every squash-merge to `master` with a `feat`/`fix`/etc. title updates a standing release-please PR (which accumulates the changelog and version bump); merging *that* PR creates a GitHub Release and tag, which triggers a build and an OIDC-authenticated publish to PyPI — no stored PyPI token, ever.

For the v1.0.0 launch specifically, this starts in **release-candidate mode**: `release-please-config.json` is configured with `versioning: "prerelease"`, `prerelease: true`, `prerelease-type: "rc"`, so every release-please PR merged while this config is active produces `1.0.0-rc.1`, `1.0.0-rc.2`, etc. (SemVer strings that `packaging.version.Version` normalizes to PEP 440 `1.0.0rc1`, `1.0.0rc2` — confirmed locally during planning). Each RC is a real GitHub prerelease and a real PyPI prerelease: installable with `pip install --pre bible-translations` or an exact version pin, but **invisible to a plain `pip install bible-translations`**, which is exactly the safe opt-in beta channel the repo owner asked for. Task 16 covers iterating through RCs; Task 17 (user-only) covers graduating off this config to cut the real, final `1.0.0`.

**Files:**
- Create: `release-please-config.json`
- Create: `.release-please-manifest.json`
- Create: `.github/workflows/cd.yml`

- [ ] **Step 1: Write the release-please config in release-candidate mode**

```json
{
  "$schema": "https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json",
  "packages": {
    ".": {
      "release-type": "python",
      "package-name": "bible-translations",
      "changelog-path": "CHANGELOG.md",
      "bump-minor-pre-major": true,
      "bump-patch-for-minor-pre-major": false,
      "draft": false,
      "prerelease": true,
      "prerelease-type": "rc",
      "versioning": "prerelease"
    }
  }
}
```

Save as `release-please-config.json` at the repo root.

- [ ] **Step 2: Write the manifest, seeded at the current version**

```json
{
  ".": "0.1.0"
}
```

Save as `.release-please-manifest.json` at the repo root. (Task 16 forces the jump to `1.0.0-rc.1`; Task 17 later forces the graduation jump to plain `1.0.0`.)

- [ ] **Step 3: Write the release-please + build + publish workflow**

Following the Python Packaging Authority's own canonical shape for this (packaging.python.org's "Publishing package distribution releases using GitHub Actions" guide): a dedicated `build` job produces the sdist/wheel once and uploads them as a GitHub Actions artifact, and a separate `publish` job downloads that exact artifact and ships it — so the bytes that get tested are guaranteed to be the exact bytes that get published, and `gh-action-pypi-publish` can attach proper build provenance attestations.

```yaml
name: CD

on:
  push:
    branches: [master]

permissions:
  contents: write
  pull-requests: write

jobs:
  release-please:
    runs-on: ubuntu-latest
    outputs:
      release_created: ${{ steps.release.outputs.release_created }}
      tag_name: ${{ steps.release.outputs.tag_name }}
    steps:
      - uses: googleapis/release-please-action@v5
        id: release
        with:
          config-file: release-please-config.json
          manifest-file: .release-please-manifest.json

  build:
    needs: release-please
    if: ${{ needs.release-please.outputs.release_created == 'true' }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
        with:
          ref: ${{ needs.release-please.outputs.tag_name }}
      - uses: actions/setup-python@v6
        with:
          python-version: "3.14"
      - name: Install build tooling
        run: python -m pip install --upgrade pip build
      - name: Build sdist and wheel
        run: python -m build
      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  publish:
    needs: [release-please, build]
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write
      contents: write
    steps:
      - name: Download build artifacts
        uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
      - name: Upload build artifacts to the GitHub Release
        run: gh release upload ${{ needs.release-please.outputs.tag_name }} dist/* --repo ${{ github.repository }}
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Alternatives considered and why they weren't used:** python-semantic-release (more Python-native than release-please, but publishes immediately on every conventional-commit push with no PR review gate — conflicts with wanting to personally review and trigger releases); Release Drafter (a common lighter-weight GitHub convention for auto-generated release notes, but it only drafts notes from PR labels — it doesn't bump a version field in a tracked file or decide when to publish, so it doesn't cover what this task needs); setuptools_scm/hatch-vcs dynamic git-tag versioning (increasingly common and worth knowing about, but it doesn't pair cleanly with a PR-based release flow that also needs to represent `-rc.N` prerelease tags — release-please's `python` release-type, which edits a literal version string in `pyproject.toml` as part of a reviewable PR diff, is the more direct fit here).

How this flows end-to-end:
1. A squash-merged PR (e.g. `feat: add ASV translation`) lands on `master`.
2. `release-please` job runs, sees unreleased Conventional Commits since the last release, and opens/updates a standing "chore(master): release X.Y.Z-rc.N" PR containing the version bump + changelog (while `release-please-config.json` is in the release-candidate mode from Step 1 above). `release_created` is `false` on this run — nothing publishes yet.
3. Later, merging *that* release PR triggers this workflow again. This time release-please tags the release (e.g. `v1.0.0-rc.1`) and sets `release_created=true`.
4. The `publish` job (gated on that output) checks out the exact tag, builds the sdist/wheel, and publishes to PyPI using the `pypi` GitHub Environment's OIDC identity (no API token — see Task 15 for the one-time PyPI-side registration this requires), then attaches the built artifacts to the GitHub Release. Because the version string carries the `rc` prerelease marker, this publish is invisible to a plain `pip install bible-translations` — exactly as intended for a release candidate.
5. This same workflow, unmodified, later also handles the final stable `1.0.0` publish in Task 17 — only the config's prerelease settings change, not the workflow itself.

- [ ] **Step 4: Commit**

```bash
git add release-please-config.json .release-please-manifest.json .github/workflows/cd.yml
git commit -m "ci: add release-please and PyPI trusted-publishing CD workflow"
```

---

## Task 15: Manual one-time setup (PyPI Trusted Publisher + GitHub Environment)

These steps cannot be done from a git commit — they're external service configuration only the repo owner can perform. Do these **before** merging the first release-please release PR, otherwise Task 14's `publish` job will fail with an OIDC/authentication error.

- [ ] **Step 1: Create the `pypi` GitHub Environment**

In the repo's GitHub Settings → Environments, create an environment named exactly `pypi` (matches `environment: pypi` in `cd.yml`). No secrets need to be added to it — Trusted Publishing doesn't use one.

- [ ] **Step 2: Register a PyPI "pending publisher" for this project**

Since `bible-translations` isn't on PyPI yet, go to https://pypi.org/manage/account/publishing/ (requires a PyPI account) and add a **pending publisher** with:
- PyPI Project Name: `bible-translations`
- Owner: `jadenzaleski`
- Repository name: `bible-translations`
- Workflow filename: `cd.yml`
- Environment name: `pypi`

PyPI will automatically convert this into a real trusted publisher the first time `cd.yml`'s `publish` job runs successfully and claims the project name.

- [ ] **Step 3 (recommended dry run): verify the build artifact itself before trusting it to real PyPI**

This step doesn't touch the automated pipeline — it's a manual sanity check that `python -m build` produces an installable package, run once locally:

```bash
python -m build
python -m venv /tmp/bt-smoke-test
source /tmp/bt-smoke-test/bin/activate
pip install dist/bible_translations-*.whl
bt --version
bt verse "John 3:16"
deactivate
rm -rf /tmp/bt-smoke-test
```

Expected: `bt --version` prints the version, and `bt verse "John 3:16"` successfully fetches and exports a verse.

- [ ] **Step 4: No commit for this task** — it is entirely external configuration.

---

## Task 16: Cut and iterate release candidates for v1.0.0

With everything above merged to `master`, force the first release-please PR to target `1.0.0-rc.1` instead of the natural `0.2.0` it would otherwise compute from the accumulated `feat:` commits. From there, every further `feat:`/`fix:` PR merged to `master` while Task 14's release-candidate config is active accumulates into the *next* RC automatically — this task can be repeated as many times as needed while the repo owner tests each RC.

**This task may be performed by Fable.** Cutting and publishing release candidates is exactly what they're for — low-stakes, clearly labeled as prerelease, invisible to normal installs. The hard boundary is Task 17 (the actual `1.0.0` GA), not this one.

**Files:** none (git + GitHub UI only)

- [ ] **Step 1 (manual, GitHub UI, one-time): set the repo's merge strategy**

In Settings → General → Pull Requests, enable **Allow squash merging** and disable (or at least stop defaulting to) merge commits and rebase merging, so every PR's squash commit message is exactly its title — this is what makes Task 13's PR-title lint meaningful and what release-please parses.

- [ ] **Step 2: Confirm all prior tasks' PRs are merged to `master`**

```bash
git checkout master
git pull origin master
pytest -m "not live" -q
ruff check .
```

Expected: all fast tests pass, no lint errors.

- [ ] **Step 3: Push an explicit release-override commit to seed the first RC**

```bash
git commit --allow-empty -m "chore: release 1.0.0-rc.1" -m "Release-As: 1.0.0-rc.1"
git push origin master
```

This triggers `cd.yml`'s `release-please` job, which — because of the `Release-As:` footer plus Task 14's `prerelease`/`versioning` config — opens the standing release PR targeting `1.0.0-rc.1` instead of the next natural semver bump.

- [ ] **Step 4: Review and merge the release-please PR to publish the RC**

release-please will have opened a PR titled something like `chore(master): release 1.0.0-rc.1` containing the version bump in `pyproject.toml` and `.release-please-manifest.json`, plus a generated `CHANGELOG.md` entry. Review it, then squash-merge it. `cd.yml` then tags `v1.0.0-rc.1`, marks the GitHub Release as a prerelease, and publishes `bible-translations==1.0.0rc1` to PyPI.

- [ ] **Step 5: Verify the RC installs correctly and is invisible to normal installs**

```bash
pip index versions bible-translations
pip install --no-cache-dir --pre bible-translations==1.0.0rc1
bt --version
bt verse "John 3:16" -t ASV
```

Then, in a **fresh virtual environment** (reusing the one above would just report "already satisfied" against the prerelease already installed there, which proves nothing), confirm a plain install does *not* pick up the RC:

```bash
python -m venv /tmp/bt-plain-install-check
source /tmp/bt-plain-install-check/bin/activate
pip install --no-cache-dir bible-translations
pip show bible-translations | grep Version
deactivate
rm -rf /tmp/bt-plain-install-check
```

Expected: the plain install either fails (nothing stable published yet) or, once a prior stable version exists, resolves to that stable version — never to `1.0.0rc1`.

- [ ] **Step 6: Iterate on further RCs as needed**

For any further fixes/features discovered while testing `1.0.0-rc.1`, merge normal `feat:`/`fix:` PRs to `master` as usual (no `Release-As:` needed — the prerelease config keeps auto-incrementing: `1.0.0-rc.2`, `1.0.0-rc.3`, ...). Repeat Steps 4–5 for each new RC. Stay on this task, cutting as many RCs as the repo owner wants to test, until they say they're satisfied and ready to move to Task 17.

No routine commit for this task beyond the `Release-As` seed in Step 3 — subsequent RCs come from ordinary feature/fix PRs.

---

## Task 17: Graduate to the stable v1.0.0 release

**This task is performed entirely by the repo owner. Do not execute any step in this task as an autonomous agent — prepare nothing beyond what Task 16 already produced, and stop here.** The whole point of the release-candidate channel in Tasks 14 and 16 was to let the owner validate everything *before* the one irreversible step: cutting the actual, permanent `v1.0.0` that a plain `pip install bible-translations` will forever after resolve to by default.

**Files:**
- Modify: `release-please-config.json` (owner edits, not Fable)
- Modify: `pyproject.toml` (owner edits, not Fable)

- [ ] **Step 1: Turn off release-candidate mode**

In `release-please-config.json`, remove the three prerelease-related keys added in Task 14:

```json
{
  "$schema": "https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json",
  "packages": {
    ".": {
      "release-type": "python",
      "package-name": "bible-translations",
      "changelog-path": "CHANGELOG.md",
      "bump-minor-pre-major": true,
      "bump-patch-for-minor-pre-major": false,
      "draft": false,
      "prerelease": false
    }
  }
}
```

(`versioning` and `prerelease-type` are removed entirely; `prerelease` goes back to `false`.)

- [ ] **Step 1b: Mark the project as stable**

In `pyproject.toml`, change the trove classifier set from Task 2:

```toml
"Development Status :: 4 - Beta",
```

to:

```toml
"Development Status :: 5 - Production/Stable",
```

- [ ] **Step 2: Commit and push the graduation override**

```bash
git add release-please-config.json pyproject.toml
git commit -m "chore: release 1.0.0" -m "Release-As: 1.0.0"
git push origin master
```

The `Release-As:` footer, combined with the now-stable config, tells release-please to stop producing `-rc.N` suffixes and target plain `1.0.0` — this is the documented release-please pattern for graduating a prerelease series to stable.

- [ ] **Step 3: Review and merge the final release-please PR**

release-please opens a PR titled `chore(master): release 1.0.0`. Review the generated `CHANGELOG.md` — it should now read as the real v1.0.0 changelog, not an RC's. Squash-merge it yourself.

- [ ] **Step 4: Watch the `cd.yml` run this merge triggers**

Confirm in the Actions tab: `release-please` job reports `release_created: true` with `tag_name: v1.0.0`, and the `publish` job builds and publishes to PyPI without error.

- [ ] **Step 5: Verify the published package**

```bash
pip install --no-cache-dir bible-translations==1.0.0
bt --version
bt verse "John 3:16" -t ASV
```

Expected: version `1.0.0` (no `rc` suffix) installs from PyPI with a plain, non-`--pre` install, and both KJV and ASV work end-to-end.

- [ ] **Step 6: Confirm the docs site reflects the release**

Visit `https://jadenzaleski.github.io/bible-translations/changelog/` and confirm the `1.0.0` entry appears.

No further commit — this task's deliverable is the published, permanent `v1.0.0` release itself.

---

## Self-Review Notes

- **Spec coverage:** every Global Constraint maps to a task — plan review gate (0), trunk consolidation (1), no bundled data (10), KJV+ASV (6), flatten in scope / paragraph-breaks out of scope (7–8, explicitly not touched), Conventional Commits (13), squash-merge (16), Ruff compliance (ongoing, unchanged config), OIDC-only PyPI (14–15), release-candidate channel (14, 16), owner-only stable graduation (17). Documentation and "tests on every PR" (explicit mid-planning requests) are covered by Tasks 11–12 and the existing `pull_request: branches: [master]` trigger retained through Task 4's `ci.yml` rewrite.
- **Placeholder scan:** all code blocks are complete, runnable snippets; no "add appropriate handling" language; every assertion in every test has a concrete expected value. The PEP 440 normalization claim in Task 14 (`1.0.0-rc.1` → `1.0.0rc1`) was verified locally with `packaging.version.Version` during planning, not assumed.
- **Type/name consistency checked:** `flatten_books`/`FlatVerse` (Task 7) match their usage in `exporter.py` (Task 8) and `__init__.py` (Task 9) exactly; `Exporter.export(..., flat=...)` signature is consistent between Task 8's implementation and its test; `VERSION` name is preserved across Task 3 so no other file needs touching.
- **Ownership boundary checked:** Task 17 is the only task in this plan that must never be executed by an agent unsupervised — every prior task, including the RC cutting in Task 16, is safe for Fable to run because nothing before Task 17 is a permanent, default-visible release.
