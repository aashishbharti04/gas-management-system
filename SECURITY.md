# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of this project seriously. If you discover a vulnerability,
**please do not open a public issue.** Instead:

1. Email **aashish@marketdoctorsonline.com** with:
   - A description of the issue and its impact.
   - Steps to reproduce (proof of concept if possible).
   - Any suggested remediation.
2. You will receive an acknowledgement within **72 hours**.
3. We will investigate, keep you informed of progress, and credit you (if you wish)
   once a fix is released.

Please give us a reasonable amount of time to remediate before any public disclosure.

## Security Practices in This Project

This application was deliberately hardened during its rewrite:

- **No hard-coded secrets.** All credentials and connection settings come from
  environment variables (`.env` is git-ignored).
- **Parameterised SQL only.** User input is never interpolated into queries,
  eliminating SQL injection.
- **Password hashing.** Passwords are stored as salted PBKDF2-HMAC-SHA256 digests,
  never in plaintext. Login uses constant-time comparison.
- **Minimal data collection.** Payment-card numbers are never collected or stored.
- **Input validation.** All user input is validated before it reaches the data layer.
- **Least surprise on errors.** Domain-specific exceptions avoid leaking internal
  database/driver details to end users.

## Hardening Recommendations for Operators

- Change the default admin credentials (`GMS_ADMIN_USERNAME` / `GMS_ADMIN_PASSWORD`)
  **before first run**.
- Restrict filesystem permissions on the SQLite database file.
- When using MySQL, create a dedicated least-privilege database user.
- Keep Python and dependencies up to date.
