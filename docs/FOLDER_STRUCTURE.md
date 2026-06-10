# Folder Structure

```
gas-management-system/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md          # Bug report issue template
│   │   ├── feature_request.md     # Feature request issue template
│   │   └── config.yml             # Issue chooser config
│   ├── workflows/
│   │   └── ci.yml                 # Lint + test (3.9–3.12, 3 OSes) + build
│   └── PULL_REQUEST_TEMPLATE.md   # PR checklist
│
├── docs/
│   ├── ARCHITECTURE.md            # Layered design & decisions
│   ├── FOLDER_STRUCTURE.md        # This file
│   ├── API.md                     # Public module/function reference
│   ├── DEPLOYMENT.md              # Install / Docker / MySQL deployment
│   └── DEVELOPMENT.md             # Local dev setup & workflow
│
├── src/
│   └── gas_management/            # The application package
│       ├── __init__.py            # Version & metadata
│       ├── __main__.py            # `python -m gas_management`
│       ├── cli.py                 # Interactive controller (flow only)
│       ├── ui.py                  # rich-based presentation & footer
│       ├── services.py            # Business logic (no I/O)
│       ├── pricing.py             # Bill calculation
│       ├── validators.py          # Input validation
│       ├── auth.py                # Password hashing & authentication
│       ├── models.py              # Dataclasses: User, Customer, Bill, GasType
│       ├── config.py              # Env-based Settings + .env loader
│       ├── exceptions.py          # Domain exception hierarchy
│       ├── py.typed               # PEP 561 type marker
│       └── db/                    # Persistence layer
│           ├── __init__.py        # Exposes Repository + factory
│           ├── base.py            # Abstract Repository + shared SQLRepository
│           ├── sqlite_repo.py     # SQLite backend (default)
│           ├── mysql_repo.py      # MySQL backend (optional)
│           └── factory.py         # Backend selector
│
├── tests/
│   ├── conftest.py                # Shared fixtures (in-memory repo, settings)
│   ├── test_auth.py               # Hashing & login tests
│   ├── test_validators.py         # Input validation tests
│   ├── test_pricing.py            # Billing calculation tests
│   └── test_repository.py         # Repository + services integration tests
│
├── .env.example                   # Sample configuration (copy to .env)
├── .gitignore
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE                        # MIT
├── README.md
├── SECURITY.md
├── pyproject.toml                 # Packaging, deps, tooling config
├── requirements.txt               # Runtime dependency (rich)
└── requirements-dev.txt           # Dev dependencies (pytest, ruff)
```

## Conventions

- **`src/` layout** keeps the importable package isolated from the repo root,
  preventing accidental imports of un-installed code and matching modern packaging
  best practice.
- **One responsibility per module** — see [ARCHITECTURE.md](ARCHITECTURE.md).
- **Tests mirror the package** so it is obvious where coverage lives.
