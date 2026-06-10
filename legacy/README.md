# Legacy prototype (archived)

These files are the **original prototype** of the Gas Management System, preserved
here for historical reference only. **They are not used by the application and are
excluded from linting, testing, and packaging.**

The current, supported implementation lives in [`../src/gas_management/`](../src/gas_management).

## Why they were replaced

The original scripts had serious problems that the rewrite resolved:

- Hard-coded database passwords committed to source.
- SQL injection via string-formatted queries.
- Plaintext, hard-coded login (one variant raised `NameError` on startup).
- Storage of payment-card numbers.
- Billing that never actually updated records (queries referenced literal strings).
- A malformed `CREATE TABLE` statement and INSERT column mismatches.
- Five overlapping, duplicated files.

See the project [CHANGELOG](../CHANGELOG.md) for the full list of fixes.

## Files

| File | Original purpose |
| ---- | ---------------- |
| `main gas.py` | The most complete prototype (login + menu). |
| `main gas file1.py` | Early menu/login variant. |
| `main gas file2.py` | Table creation snippet. |
| `main gas file 3.py` | Connection + cursor snippet. |
| `gas managent 1.py` | Table creation snippet. |
| `6060 gas management system.docx` | Original project report. |
