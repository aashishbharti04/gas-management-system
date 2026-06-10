"""Application configuration.

All configuration is sourced from environment variables (optionally loaded from a
local ``.env`` file). Nothing sensitive is ever hard-coded in the source tree.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .exceptions import ConfigurationError


def load_dotenv(path: str | os.PathLike[str] | None = None) -> None:
    """Populate ``os.environ`` from a ``.env`` file if present.

    Prefers ``python-dotenv`` when installed; otherwise falls back to a small,
    dependency-free parser. Existing environment variables are never overwritten.
    """
    try:  # pragma: no cover - exercised only when python-dotenv is installed
        from dotenv import load_dotenv as _load

        _load(dotenv_path=path)
        return
    except Exception:
        pass

    env_path = Path(path) if path else Path.cwd() / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _get_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be a number, got {raw!r}") from exc


def _get_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be an integer, got {raw!r}") from exc


@dataclass(frozen=True)
class Settings:
    """Immutable, validated application settings."""

    # Storage backend: "sqlite" (default, zero-config) or "mysql".
    db_backend: str = "sqlite"
    sqlite_path: str = "gas_management.db"

    # MySQL connection (only used when db_backend == "mysql").
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_database: str = "gasin"

    # Pricing (currency units per litre).
    cng_price: float = 75.0
    lpg_price: float = 80.0
    currency_symbol: str = "Rs."

    # Default administrator seeded on first run when no users exist.
    # Override these in your environment; the seeded password is hashed at rest.
    admin_username: str = "admin"
    admin_password: str = "admin123"

    # Web dashboard settings (used by the optional FastAPI front-end).
    web_host: str = "127.0.0.1"
    web_port: int = 8000
    web_secret_key: str = ""  # used to sign session cookies; auto-generated if empty
    web_cookie_secure: bool = False  # set True when serving over HTTPS

    @classmethod
    def from_env(cls) -> Settings:
        """Build settings from the current environment."""
        backend = os.environ.get("GMS_DB_BACKEND", "sqlite").strip().lower()
        if backend not in {"sqlite", "mysql"}:
            raise ConfigurationError(f"GMS_DB_BACKEND must be 'sqlite' or 'mysql', got {backend!r}")
        return cls(
            db_backend=backend,
            sqlite_path=os.environ.get("GMS_SQLITE_PATH", "gas_management.db"),
            mysql_host=os.environ.get("GMS_MYSQL_HOST", "localhost"),
            mysql_port=_get_int("GMS_MYSQL_PORT", 3306),
            mysql_user=os.environ.get("GMS_MYSQL_USER", "root"),
            mysql_password=os.environ.get("GMS_MYSQL_PASSWORD", ""),
            mysql_database=os.environ.get("GMS_MYSQL_DATABASE", "gasin"),
            cng_price=_get_float("GMS_CNG_PRICE", 75.0),
            lpg_price=_get_float("GMS_LPG_PRICE", 80.0),
            currency_symbol=os.environ.get("GMS_CURRENCY_SYMBOL", "Rs."),
            admin_username=os.environ.get("GMS_ADMIN_USERNAME", "admin"),
            admin_password=os.environ.get("GMS_ADMIN_PASSWORD", "admin123"),
            web_host=os.environ.get("GMS_WEB_HOST", "127.0.0.1"),
            web_port=_get_int("GMS_WEB_PORT", 8000),
            web_secret_key=os.environ.get("GMS_WEB_SECRET_KEY", ""),
            web_cookie_secure=_get_bool("GMS_WEB_COOKIE_SECURE", False),
        )
