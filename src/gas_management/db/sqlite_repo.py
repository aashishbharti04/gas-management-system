"""SQLite storage backend (default, zero-configuration)."""

from __future__ import annotations

import sqlite3

from .base import SQLRepository


class SQLiteRepository(SQLRepository):
    """Stores data in a local SQLite database file."""

    placeholder = "?"

    def __init__(self, path: str = "gas_management.db") -> None:
        super().__init__()
        self._path = path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _schema_statements(self) -> list[str]:
        return [
            """
            CREATE TABLE IF NOT EXISTS users (
                username      TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                created_at    TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS customers (
                account_no     TEXT PRIMARY KEY,
                name           TEXT NOT NULL,
                address        TEXT NOT NULL,
                phone          TEXT DEFAULT '',
                cng_litres     REAL NOT NULL DEFAULT 0,
                lpg_litres     REAL NOT NULL DEFAULT 0,
                amount_due     REAL NOT NULL DEFAULT 0,
                credit_balance REAL NOT NULL DEFAULT 0,
                created_at     TEXT NOT NULL,
                updated_at     TEXT NOT NULL
            )
            """,
            "CREATE INDEX IF NOT EXISTS idx_customers_name ON customers (name)",
        ]
