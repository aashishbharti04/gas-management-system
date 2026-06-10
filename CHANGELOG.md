# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- _Nothing yet._

## [1.0.0] - 2026-06-10

The first stable, production-ready release. The original single-file prototype was
re-engineered into a secure, tested, modular Python package while preserving every
user-facing feature.

### Added
- Modular package under `src/gas_management/` with clear layers
  (config, models, validators, auth, services, storage, UI, CLI).
- **SQLite** storage backend (default, zero-configuration).
- Optional **MySQL** backend selectable via configuration.
- Backend-agnostic `Repository` interface with a shared, parameterised SQL implementation.
- Secure authentication using salted **PBKDF2-HMAC-SHA256** password hashing.
- First-run seeding of a configurable default administrator.
- Input validation for names, account numbers, addresses, phone, amounts and litres.
- Premium terminal UI (`rich`): banner, menu, tables, loading spinners, and
  success/warning/error/empty states, plus a professional footer.
- Customer **search**, **list**, **view**, and **delete** operations.
- Configurable pricing and currency symbol via environment variables.
- Full `pytest` test suite (auth, validators, pricing, repository/services).
- Packaging via `pyproject.toml` with a `gas-management` console entry point.
- Open-source scaffolding: README, LICENSE (MIT), CONTRIBUTING, CODE_OF_CONDUCT,
  SECURITY, issue/PR templates, GitHub Actions CI, and architecture/deployment docs.

### Changed
- Billing logic now works correctly and persists balance changes (the original
  updates silently referenced literal strings and never updated records).
- Credentials and database settings are sourced from environment variables instead
  of being hard-coded.
- UTF-8 console output is enforced for reliable rendering on Windows.

### Fixed
- **SQL injection**: all queries are now parameterised (was string-formatted).
- **Hard-coded database password** removed from source.
- **Plaintext / crashing login** (`username == akash` raised `NameError`) replaced
  with a secure, hashed authentication flow.
- Malformed `CREATE TABLE` (missing parenthesis) and INSERT column mismatches.
- Numerous typos and logic bugs (`updata`, `amont`, `records`/`record`, undefined
  `v_credit`) eliminated by the rewrite.

### Security
- Payment-card numbers are **no longer collected or stored**.
- Constant-time password comparison and user-enumeration mitigation on login.

### Removed
- Duplicate prototype scripts consolidated into a single, coherent package.

[Unreleased]: https://github.com/aashishbharti04/gas-management-system/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/aashishbharti04/gas-management-system/releases/tag/v1.0.0
