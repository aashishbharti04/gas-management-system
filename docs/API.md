# API Reference

The Gas Management System is a CLI, but its internal modules form a clean,
reusable API. This reference documents the public surface you would use to embed
the logic in another front-end (e.g. a web service).

## `gas_management.config`

### `Settings`
Immutable dataclass of validated configuration.

| Field | Type | Default |
| ----- | ---- | ------- |
| `db_backend` | `str` | `"sqlite"` |
| `sqlite_path` | `str` | `"gas_management.db"` |
| `mysql_host/port/user/password/database` | — | see `.env.example` |
| `cng_price` / `lpg_price` | `float` | `75.0` / `80.0` |
| `currency_symbol` | `str` | `"Rs."` |
| `admin_username` / `admin_password` | `str` | `"admin"` / `"admin123"` |

- `Settings.from_env() -> Settings` — build from environment variables.

### `load_dotenv(path=None) -> None`
Populate `os.environ` from a `.env` file (uses `python-dotenv` if available).

## `gas_management.models`

- `GasType` — `Enum`: `CNG`, `LPG`, `BOTH`.
- `User(username, password_hash, created_at)`
- `Customer(account_no, name, address, phone, cng_litres, lpg_litres, amount_due, credit_balance, created_at, updated_at)`
- `Bill(gas_type, cng_litres, lpg_litres, cng_amount, lpg_amount)` — `.total` property.

## `gas_management.auth`

- `hash_password(password, *, iterations=240000) -> str` — salted PBKDF2 digest string.
- `verify_password(password, stored) -> bool` — constant-time verification.
- `authenticate(username, password, user) -> User` — raises `AuthenticationError`.

## `gas_management.validators`

All raise `ValidationError` on bad input and return the normalised value:

- `validate_name(value) -> str`
- `validate_account_no(value) -> str`
- `validate_address(value) -> str`
- `validate_phone(value) -> str`
- `validate_amount(value, *, field="Amount") -> float`
- `validate_litres(value) -> float`

## `gas_management.pricing`

- `compute_bill(settings, gas_type, *, cng_litres=0.0, lpg_litres=0.0) -> Bill`

## `gas_management.services`

High-level use cases (no console I/O):

- `seed_default_admin(repo, settings) -> bool`
- `login(repo, username, password) -> User`
- `create_customer(repo, *, account_no, name, address, phone="", credit_balance=0.0) -> Customer`
- `record_purchase(repo, settings, *, account_no, gas_type, cng_litres=0.0, lpg_litres=0.0, pay_from_credit=False) -> tuple[Customer, Bill]`

## `gas_management.db`

### `Repository` (abstract)
- `initialize()`, `close()`
- `get_user(username)`, `create_user(user)`, `count_users()`
- `add_customer(customer)`, `get_customer(account_no)`, `list_customers()`,
  `search_customers(term)`, `update_customer(customer)`, `delete_customer(account_no)`
- Usable as a context manager (`with create_repository(settings) as repo:`).

### `create_repository(settings) -> Repository`
Returns a `SQLiteRepository` or `MySQLRepository` based on `settings.db_backend`.

## Exceptions (`gas_management.exceptions`)

```
GasManagementError
├── ConfigurationError
├── ValidationError
├── AuthenticationError
└── RepositoryError
    ├── CustomerNotFoundError
    └── DuplicateCustomerError
```

## Example: programmatic use

```python
from gas_management.config import Settings
from gas_management.db import create_repository
from gas_management.services import create_customer, record_purchase, seed_default_admin
from gas_management.models import GasType

settings = Settings.from_env()
with create_repository(settings) as repo:
    seed_default_admin(repo, settings)
    create_customer(repo, account_no="ACC1", name="Asha", address="12 Road")
    customer, bill = record_purchase(
        repo, settings, account_no="ACC1", gas_type=GasType.CNG, cng_litres=2
    )
    print(customer.amount_due, bill.total)  # 150.0 150.0
```
