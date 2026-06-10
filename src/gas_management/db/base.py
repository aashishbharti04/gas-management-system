"""Backend-agnostic repository interface and shared SQL implementation.

The abstract :class:`Repository` defines the storage contract. :class:`SQLRepository`
implements every data-manipulation query *once* using a configurable parameter
placeholder, so the SQLite and MySQL backends only differ in connection handling
and schema DDL. Every query is parameterised — there is no string interpolation
of user data, which eliminates the SQL-injection class of bugs from the original.
"""

from __future__ import annotations

import abc
from datetime import datetime

from ..exceptions import (
    CustomerNotFoundError,
    DuplicateCustomerError,
    RepositoryError,
)
from ..models import Customer, User


class Repository(abc.ABC):
    """Abstract storage contract used by the rest of the application."""

    # --- lifecycle -----------------------------------------------------
    @abc.abstractmethod
    def initialize(self) -> None:
        """Create tables if they do not already exist."""

    @abc.abstractmethod
    def close(self) -> None:
        """Release the underlying connection."""

    # --- users ---------------------------------------------------------
    @abc.abstractmethod
    def get_user(self, username: str) -> User | None: ...

    @abc.abstractmethod
    def create_user(self, user: User) -> None: ...

    @abc.abstractmethod
    def count_users(self) -> int: ...

    # --- customers -----------------------------------------------------
    @abc.abstractmethod
    def add_customer(self, customer: Customer) -> None: ...

    @abc.abstractmethod
    def get_customer(self, account_no: str) -> Customer | None: ...

    @abc.abstractmethod
    def list_customers(self) -> list[Customer]: ...

    @abc.abstractmethod
    def search_customers(self, term: str) -> list[Customer]: ...

    @abc.abstractmethod
    def update_customer(self, customer: Customer) -> None: ...

    @abc.abstractmethod
    def delete_customer(self, account_no: str) -> None: ...

    # --- context manager ----------------------------------------------
    def __enter__(self) -> Repository:
        self.initialize()
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()


class SQLRepository(Repository):
    """Shared SQL implementation parameterised by placeholder style.

    Subclasses must provide :attr:`placeholder` (``"?"`` or ``"%s"``), a live
    DB-API connection via :meth:`_connect`, and the schema DDL via
    :meth:`_schema_statements`.
    """

    placeholder: str = "?"

    def __init__(self) -> None:
        self._conn = None

    # -- to be provided by subclasses ----------------------------------
    @abc.abstractmethod
    def _connect(self):
        """Return a live DB-API 2.0 connection."""

    @abc.abstractmethod
    def _schema_statements(self) -> list[str]:
        """Return the CREATE TABLE statements for this backend."""

    # -- helpers --------------------------------------------------------
    @property
    def conn(self):
        if self._conn is None:
            self._conn = self._connect()
        return self._conn

    def _q(self, sql: str) -> str:
        """Adapt ``?`` placeholders in shared SQL to the backend's style."""
        if self.placeholder == "?":
            return sql
        return sql.replace("?", self.placeholder)

    @staticmethod
    def _row_to_customer(row: tuple) -> Customer:
        return Customer(
            account_no=row[0],
            name=row[1],
            address=row[2],
            phone=row[3] or "",
            cng_litres=float(row[4]),
            lpg_litres=float(row[5]),
            amount_due=float(row[6]),
            credit_balance=float(row[7]),
            created_at=_as_datetime(row[8]),
            updated_at=_as_datetime(row[9]),
        )

    # -- lifecycle ------------------------------------------------------
    def initialize(self) -> None:
        try:
            cur = self.conn.cursor()
            for statement in self._schema_statements():
                cur.execute(statement)
            self.conn.commit()
            cur.close()
        except Exception as exc:  # pragma: no cover - backend specific
            raise RepositoryError(f"Failed to initialise database: {exc}") from exc

    def close(self) -> None:
        if self._conn is not None:
            try:
                self._conn.close()
            finally:
                self._conn = None

    # -- users ----------------------------------------------------------
    def get_user(self, username: str) -> User | None:
        cur = self.conn.cursor()
        cur.execute(
            self._q("SELECT username, password_hash, created_at FROM users WHERE username = ?"),
            (username,),
        )
        row = cur.fetchone()
        cur.close()
        if row is None:
            return None
        return User(username=row[0], password_hash=row[1], created_at=_as_datetime(row[2]))

    def create_user(self, user: User) -> None:
        try:
            cur = self.conn.cursor()
            cur.execute(
                self._q("INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)"),
                (user.username, user.password_hash, user.created_at.isoformat()),
            )
            self.conn.commit()
            cur.close()
        except Exception as exc:
            raise RepositoryError(f"Could not create user: {exc}") from exc

    def count_users(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        count = int(cur.fetchone()[0])
        cur.close()
        return count

    # -- customers ------------------------------------------------------
    _CUSTOMER_COLUMNS = (
        "account_no, name, address, phone, cng_litres, lpg_litres, "
        "amount_due, credit_balance, created_at, updated_at"
    )

    def add_customer(self, customer: Customer) -> None:
        if self.get_customer(customer.account_no) is not None:
            raise DuplicateCustomerError(
                f"A customer with account number {customer.account_no!r} already exists."
            )
        try:
            cur = self.conn.cursor()
            cur.execute(
                self._q(
                    f"INSERT INTO customers ({self._CUSTOMER_COLUMNS}) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                ),
                (
                    customer.account_no,
                    customer.name,
                    customer.address,
                    customer.phone,
                    customer.cng_litres,
                    customer.lpg_litres,
                    customer.amount_due,
                    customer.credit_balance,
                    customer.created_at.isoformat(),
                    customer.updated_at.isoformat(),
                ),
            )
            self.conn.commit()
            cur.close()
        except DuplicateCustomerError:
            raise
        except Exception as exc:
            raise RepositoryError(f"Could not add customer: {exc}") from exc

    def get_customer(self, account_no: str) -> Customer | None:
        cur = self.conn.cursor()
        cur.execute(
            self._q(f"SELECT {self._CUSTOMER_COLUMNS} FROM customers WHERE account_no = ?"),
            (account_no,),
        )
        row = cur.fetchone()
        cur.close()
        return self._row_to_customer(row) if row else None

    def list_customers(self) -> list[Customer]:
        cur = self.conn.cursor()
        cur.execute(self._q(f"SELECT {self._CUSTOMER_COLUMNS} FROM customers ORDER BY name"))
        rows = cur.fetchall()
        cur.close()
        return [self._row_to_customer(r) for r in rows]

    def search_customers(self, term: str) -> list[Customer]:
        like = f"%{term}%"
        cur = self.conn.cursor()
        cur.execute(
            self._q(
                f"SELECT {self._CUSTOMER_COLUMNS} FROM customers "
                "WHERE name LIKE ? OR account_no LIKE ? ORDER BY name"
            ),
            (like, like),
        )
        rows = cur.fetchall()
        cur.close()
        return [self._row_to_customer(r) for r in rows]

    def update_customer(self, customer: Customer) -> None:
        customer.updated_at = datetime.now()
        try:
            cur = self.conn.cursor()
            cur.execute(
                self._q(
                    "UPDATE customers SET name = ?, address = ?, phone = ?, "
                    "cng_litres = ?, lpg_litres = ?, amount_due = ?, "
                    "credit_balance = ?, updated_at = ? WHERE account_no = ?"
                ),
                (
                    customer.name,
                    customer.address,
                    customer.phone,
                    customer.cng_litres,
                    customer.lpg_litres,
                    customer.amount_due,
                    customer.credit_balance,
                    customer.updated_at.isoformat(),
                    customer.account_no,
                ),
            )
            if cur.rowcount == 0:
                raise CustomerNotFoundError(
                    f"No customer with account number {customer.account_no!r}."
                )
            self.conn.commit()
            cur.close()
        except CustomerNotFoundError:
            raise
        except Exception as exc:
            raise RepositoryError(f"Could not update customer: {exc}") from exc

    def delete_customer(self, account_no: str) -> None:
        try:
            cur = self.conn.cursor()
            cur.execute(self._q("DELETE FROM customers WHERE account_no = ?"), (account_no,))
            if cur.rowcount == 0:
                raise CustomerNotFoundError(f"No customer with account number {account_no!r}.")
            self.conn.commit()
            cur.close()
        except CustomerNotFoundError:
            raise
        except Exception as exc:
            raise RepositoryError(f"Could not delete customer: {exc}") from exc


def _as_datetime(value: object) -> datetime:
    """Coerce a stored timestamp (ISO string or native datetime) to datetime."""
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return datetime.now()
    return datetime.now()
