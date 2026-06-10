# Contributing to Gas Management System

First off — thank you for taking the time to contribute! 🎉
This document explains how to get set up and the conventions we follow.

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating you
are expected to uphold it. Please report unacceptable behaviour to
**aashish@marketdoctorsonline.com**.

## Ways to Contribute

- 🐛 Report bugs using the **Bug Report** issue template.
- 💡 Suggest features using the **Feature Request** issue template.
- 📝 Improve documentation.
- 🔧 Submit code via pull requests.

## Development Setup

```bash
# Fork & clone your fork
git clone https://github.com/<your-username>/gas-management-system.git
cd gas-management-system

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install in editable mode with dev tools
pip install -e ".[dev]"
```

## Project Layout

See [docs/FOLDER_STRUCTURE.md](docs/FOLDER_STRUCTURE.md) and
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full picture. In brief:

```
src/gas_management/   # application package
  ├─ db/              # storage backends (SQLite / MySQL)
  ├─ services.py      # business logic (no I/O — easy to test)
  ├─ cli.py / ui.py   # presentation layer
  └─ ...
tests/                # pytest suite
docs/                 # architecture & guides
```

## Coding Standards

- **Style & linting:** [Ruff](https://github.com/astral-sh/ruff). Run before pushing:
  ```bash
  ruff check .
  ruff format .
  ```
- **Type hints:** use them for all new public functions.
- **Keep layers separated:** business rules go in `services.py` (no `print`/`input`);
  the UI lives in `ui.py`/`cli.py`; persistence in `db/`.
- **Security:** never interpolate user input into SQL — always use parameters.
  Never commit secrets; configuration comes from environment variables.

## Testing

All changes should be covered by tests where practical.

```bash
pytest            # run the suite
pytest --cov      # with coverage
```

Please ensure `ruff check .` and `pytest` both pass before opening a PR.

## Commit Messages

Use clear, present-tense messages. [Conventional Commits](https://www.conventionalcommits.org/)
are appreciated but not required, e.g.:

```
feat: add customer search by phone number
fix: prevent negative credit balances
docs: clarify MySQL setup
```

## Pull Request Process

1. Create a feature branch: `git checkout -b feat/my-feature`.
2. Make your change with tests and docs.
3. Ensure CI passes locally (`ruff check .` && `pytest`).
4. Open a PR using the template and link any related issue.
5. A maintainer will review and merge once approved.

## Updating the Changelog

Add a bullet to the **Unreleased** section of [CHANGELOG.md](CHANGELOG.md) describing
your change.

Thanks again! 💛
