# Architecture

This document describes how the Gas Management System is structured and why.

## Goals

- **Separation of concerns** — presentation, business logic, and persistence are
  independent and individually testable.
- **Security by construction** — no hard-coded secrets, no string-built SQL.
- **Backend flexibility** — swap SQLite for MySQL without touching business logic.

## Layered design

```
┌──────────────────────────────────────────────────────────┐
│                     Presentation                         │
│   cli.py  ──drives──▶  ui.py (rich: banner, menu, tables) │
└───────────────┬──────────────────────────────────────────┘
                │ calls (plain data in/out, no I/O)
┌───────────────▼──────────────────────────────────────────┐
│                     Business logic                       │
│   services.py · pricing.py · validators.py · auth.py      │
│   models.py (dataclasses) · config.py · exceptions.py     │
└───────────────┬──────────────────────────────────────────┘
                │ Repository interface (abstract)
┌───────────────▼──────────────────────────────────────────┐
│                      Persistence                         │
│   db/base.py (SQLRepository) ─┬─ db/sqlite_repo.py        │
│                               └─ db/mysql_repo.py         │
│   db/factory.py selects the backend from configuration    │
└──────────────────────────────────────────────────────────┘
```

### Presentation layer (`cli.py`, `ui.py`)

- `ui.py` owns **all** formatting: the banner, menus, tables, prompts, spinners
  (loading states), and success/warning/error/empty states, plus the footer.
- `cli.py` is the controller: it sequences prompts, calls services, and renders
  results. It contains no SQL and no business rules.

### Business layer

- `services.py` holds the use cases (`login`, `create_customer`, `record_purchase`,
  `seed_default_admin`). **It performs no console I/O**, so it can be unit-tested and
  reused by another front-end (e.g. a web API).
- `pricing.py` computes bills; `validators.py` validates/normalises input;
  `auth.py` handles password hashing and verification.
- `models.py` defines plain `dataclass` domain objects (`User`, `Customer`, `Bill`).
- `config.py` builds an immutable `Settings` object from environment variables.
- `exceptions.py` defines a domain-specific exception hierarchy.

### Persistence layer (`db/`)

- `base.py` defines the abstract `Repository` contract **and** a concrete
  `SQLRepository` that implements every data-manipulation query *once* using a
  configurable placeholder (`?` for SQLite, `%s` for MySQL). This removes duplication.
- `sqlite_repo.py` and `mysql_repo.py` only supply connection handling and schema DDL.
- `factory.py` returns the right backend based on `Settings.db_backend`.

## Key design decisions

| Decision | Rationale |
| -------- | --------- |
| Shared `SQLRepository` | One implementation of CRUD → no duplicate SQL across backends. |
| Parameterised queries only | Eliminates SQL injection (the original's biggest flaw). |
| Env-based config | Keeps secrets out of source control; 12-factor friendly. |
| PBKDF2 password hashing | Industry-standard, salted, tunable work factor. |
| `services.py` free of I/O | Pure functions are trivial to test and reuse. |
| `rich` UI behind `ui.py` | Centralised theming; easy to restyle or replace. |

## Data flow example: recording a purchase

1. `cli._action_record_purchase` collects and validates input via `validators`.
2. It calls `services.record_purchase(repo, settings, ...)`.
3. The service computes the bill (`pricing.compute_bill`), updates the `Customer`
   dataclass, and persists it through the `Repository`.
4. `cli` renders the invoice and updated customer via `ui`.

## Testing strategy

- **Unit tests** cover `auth`, `validators`, and `pricing` in isolation.
- **Integration tests** exercise `services` against an in-memory SQLite repository,
  validating real persistence behaviour without external dependencies.
- CI runs the suite across Python 3.9–3.12 on Linux, Windows, and macOS.
