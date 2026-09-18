# Contributing
Thanks for your interest in contributing.

## Steps
1. Fork the repo and create a new branch (preferably linking to the issue):
   ```bash
   git checkout -b 42-your-feature
   ```
2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Run the linter and formatter before committing ([ruff docs](https://docs.astral.sh/ruff/linter/)):
   ```bash
   ruff check . --fix
   ruff format
   ```
4. Run tests to verify your changes:
   ```bash
   pytest
   ```
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
6. Push and open a Pull Request to `master`.
7. Link related issues (e.g., `Closes #42`).

PRs are merged with **Squash and merge** — your PR title becomes the commit message on `master`,
so it must itself follow Conventional Commits.

## Guidelines
* Keep PRs small and focused.
* Match the existing code style (Ruff-enforced).
* Add or update tests when needed.
* Update documentation if behavior changes.

By contributing, you agree your code is under the project’s [license](LICENSE).