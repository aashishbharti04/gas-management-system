# Development Setup Guide

## Prerequisites

- Python **3.9+**
- Git

## 1. Clone & create a virtual environment

```bash
git clone https://github.com/aashishbharti04/gas-management-system.git
cd gas-management-system

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

## 2. Install in editable mode with dev tools

```bash
pip install -e ".[dev]"
```

This installs the package plus `pytest`, `pytest-cov`, and `ruff`.

## 3. Run the app

```bash
gas-management
# or
python -m gas_management
```

For a throwaway database during development:

```bash
GMS_SQLITE_PATH=dev.db gas-management
```

## 4. Run the tests

```bash
pytest                       # quick run
pytest --cov --cov-report=term-missing   # with coverage
```

Tests use an **in-memory SQLite** database (see `tests/conftest.py`) so they are fast
and leave no artifacts.

## 5. Lint & format

```bash
ruff check .                 # lint
ruff check . --fix           # auto-fix
ruff format .                # format
ruff format --check .        # verify formatting (what CI runs)
```

## 6. Project conventions

- **Layering:** keep business logic in `services.py` (no `print`/`input`), persistence
  in `db/`, and presentation in `ui.py`/`cli.py`. See
  [ARCHITECTURE.md](ARCHITECTURE.md).
- **Security:** never interpolate user input into SQL; never commit secrets.
- **Types:** annotate new public functions.
- **Tests:** add/extend tests for any behaviour change.

## 7. Adding a new storage backend

1. Subclass `SQLRepository` in a new `db/<name>_repo.py`.
2. Set `placeholder` and implement `_connect()` and `_schema_statements()`.
3. Wire it into `db/factory.create_repository`.
4. Add tests (the existing repository tests are backend-agnostic and a good template).

## 8. Useful environment variables for development

| Variable | Purpose |
| -------- | ------- |
| `GMS_SQLITE_PATH=:memory:` | Ephemeral DB (lost on exit). |
| `GMS_CNG_PRICE` / `GMS_LPG_PRICE` | Try different pricing. |
| `NO_COLOR=1` | Verify plain-text/accessible rendering. |

## 9. Before opening a PR

- [ ] `ruff check .` and `ruff format --check .` pass
- [ ] `pytest` passes
- [ ] Docs and `CHANGELOG.md` updated
- [ ] PR uses the template and links an issue
