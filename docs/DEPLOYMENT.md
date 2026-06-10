# Deployment Guide

The Gas Management System is a single-binary-style Python CLI. "Deployment" means
installing it where operators will use it and choosing a storage backend.

## 1. Local installation (SQLite — recommended default)

```bash
git clone https://github.com/aashishbharti04/gas-management-system.git
cd gas-management-system
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install .
gas-management
```

Data is stored in `gas_management.db` in the working directory. Change the location
with `GMS_SQLITE_PATH`.

> 🔐 **Before first run:** set `GMS_ADMIN_USERNAME` and `GMS_ADMIN_PASSWORD`
> (or put them in `.env`) so the seeded admin account is secure.

## 2. Shared / networked installation (MySQL)

Use MySQL when several operators must share one dataset.

```bash
pip install ".[mysql]"

export GMS_DB_BACKEND=mysql
export GMS_MYSQL_HOST=db.internal
export GMS_MYSQL_USER=gas_app
export GMS_MYSQL_PASSWORD=*****
export GMS_MYSQL_DATABASE=gasin
gas-management
```

Create a dedicated least-privilege MySQL user:

```sql
CREATE DATABASE gasin CHARACTER SET utf8mb4;
CREATE USER 'gas_app'@'%' IDENTIFIED BY 'a-strong-password';
GRANT SELECT, INSERT, UPDATE, DELETE ON gasin.* TO 'gas_app'@'%';
FLUSH PRIVILEGES;
```

The application creates its tables automatically on first run.

## 3. Docker

A minimal image:

```dockerfile
# Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir .
# Persist the SQLite DB on a mounted volume
ENV GMS_SQLITE_PATH=/data/gas_management.db
VOLUME ["/data"]
ENTRYPOINT ["gas-management"]
```

```bash
docker build -t gas-management .
docker run -it --rm -v "$PWD/data:/data" \
  -e GMS_ADMIN_USERNAME=admin -e GMS_ADMIN_PASSWORD='change-me' \
  gas-management
```

> Use `-it` so the interactive prompts work.

## 4. Configuration via `.env`

Copy `.env.example` to `.env` and edit. The file is git-ignored and loaded
automatically at startup.

## 5. Upgrades

```bash
git pull
pip install --upgrade .
```

The schema uses `CREATE TABLE IF NOT EXISTS`, so existing data is preserved across
upgrades. Review [CHANGELOG.md](../CHANGELOG.md) for breaking changes before upgrading.

## 6. Backups

- **SQLite:** copy the `*.db` file while the app is not running.
- **MySQL:** use `mysqldump gasin > backup.sql`.

## Deployment-ready checklist

- [ ] Admin credentials changed from defaults.
- [ ] `.env` present and **not** committed.
- [ ] Database file/volume has restricted permissions.
- [ ] `pytest` and `ruff check .` pass (CI green).
- [ ] Backups scheduled.
