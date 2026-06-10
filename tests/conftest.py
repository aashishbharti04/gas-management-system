"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from gas_management.config import Settings
from gas_management.db.sqlite_repo import SQLiteRepository


@pytest.fixture()
def settings() -> Settings:
    return Settings(db_backend="sqlite", sqlite_path=":memory:")


@pytest.fixture()
def repo():
    """An initialised in-memory SQLite repository."""
    repository = SQLiteRepository(":memory:")
    repository.initialize()
    try:
        yield repository
    finally:
        repository.close()
