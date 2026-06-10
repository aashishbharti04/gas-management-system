"""Factory that selects a storage backend based on configuration."""

from __future__ import annotations

from ..config import Settings
from .base import Repository


def create_repository(settings: Settings) -> Repository:
    """Return a concrete :class:`Repository` for the configured backend."""
    if settings.db_backend == "mysql":
        from .mysql_repo import MySQLRepository

        return MySQLRepository(settings)

    from .sqlite_repo import SQLiteRepository

    return SQLiteRepository(settings.sqlite_path)
