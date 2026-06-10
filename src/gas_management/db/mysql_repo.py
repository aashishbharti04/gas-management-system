"""MySQL storage backend (optional).

Requires the ``mysql`` extra:  ``pip install gas-management-system[mysql]``.
Credentials are read from configuration/environment — never hard-coded.
"""

from __future__ import annotations

from ..config import Settings
from ..exceptions import RepositoryError
from .base import SQLRepository


class MySQLRepository(SQLRepository):
    """Stores data in a MySQL database."""

    placeholder = "%s"

    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self._settings = settings

    def _connect(self):
        try:
            import mysql.connector as mysql
        except ImportError as exc:  # pragma: no cover - depends on optional extra
            raise RepositoryError(
                "MySQL backend selected but 'mysql-connector-python' is not installed. "
                "Install it with:  pip install gas-management-system[mysql]"
            ) from exc

        s = self._settings
        try:
            return mysql.connect(
                host=s.mysql_host,
                port=s.mysql_port,
                user=s.mysql_user,
                password=s.mysql_password,
                database=s.mysql_database,
            )
        except mysql.Error as exc:  # pragma: no cover - needs a live server
            raise RepositoryError(f"Could not connect to MySQL: {exc}") from exc

    def _schema_statements(self) -> list[str]:
        return [
            """
            CREATE TABLE IF NOT EXISTS users (
                username      VARCHAR(40) PRIMARY KEY,
                password_hash VARCHAR(255) NOT NULL,
                created_at    VARCHAR(40) NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS customers (
                account_no     VARCHAR(20) PRIMARY KEY,
                name           VARCHAR(40) NOT NULL,
                address        VARCHAR(120) NOT NULL,
                phone          VARCHAR(20) DEFAULT '',
                cng_litres     DOUBLE NOT NULL DEFAULT 0,
                lpg_litres     DOUBLE NOT NULL DEFAULT 0,
                amount_due     DOUBLE NOT NULL DEFAULT 0,
                credit_balance DOUBLE NOT NULL DEFAULT 0,
                created_at     VARCHAR(40) NOT NULL,
                updated_at     VARCHAR(40) NOT NULL,
                INDEX idx_customers_name (name)
            )
            """,
        ]
