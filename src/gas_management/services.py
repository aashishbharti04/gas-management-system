"""Application services: business logic that sits between the UI and storage.

Keeping this layer free of any I/O (no ``input``/``print``) makes the core logic
straightforward to unit-test and reuse from a different front-end (e.g. a web API).
"""

from __future__ import annotations

from .auth import authenticate, hash_password
from .config import Settings
from .db import Repository
from .exceptions import ValidationError
from .models import Bill, Customer, GasType, User
from .pricing import compute_bill


def seed_default_admin(repo: Repository, settings: Settings) -> bool:
    """Create the default admin account if no users exist yet.

    Returns ``True`` if an account was seeded.
    """
    if repo.count_users() > 0:
        return False
    repo.create_user(
        User(
            username=settings.admin_username,
            password_hash=hash_password(settings.admin_password),
        )
    )
    return True


def login(repo: Repository, username: str, password: str) -> User:
    """Authenticate a user, raising :class:`AuthenticationError` on failure."""
    return authenticate(username, password, repo.get_user(username))


def create_customer(
    repo: Repository,
    *,
    account_no: str,
    name: str,
    address: str,
    phone: str = "",
    credit_balance: float = 0.0,
) -> Customer:
    """Create and persist a new customer account."""
    customer = Customer(
        account_no=account_no,
        name=name,
        address=address,
        phone=phone,
        credit_balance=credit_balance,
    )
    repo.add_customer(customer)
    return customer


def record_purchase(
    repo: Repository,
    settings: Settings,
    *,
    account_no: str,
    gas_type: GasType,
    cng_litres: float = 0.0,
    lpg_litres: float = 0.0,
    pay_from_credit: bool = False,
) -> tuple[Customer, Bill]:
    """Record a gas purchase for a customer and update their balances.

    The bill is added to ``amount_due``; when ``pay_from_credit`` is set, the
    total is also deducted from the customer's ``credit_balance`` and the due
    amount is cleared accordingly. Litres are accumulated on the customer record.
    """
    customer = repo.get_customer(account_no)
    if customer is None:
        from .exceptions import CustomerNotFoundError

        raise CustomerNotFoundError(f"No customer with account number {account_no!r}.")

    bill = compute_bill(settings, gas_type, cng_litres=cng_litres, lpg_litres=lpg_litres)

    customer.cng_litres = round(customer.cng_litres + bill.cng_litres, 2)
    customer.lpg_litres = round(customer.lpg_litres + bill.lpg_litres, 2)

    if pay_from_credit:
        if bill.total > customer.credit_balance:
            raise ValidationError(
                f"Insufficient credit balance "
                f"({settings.currency_symbol}{customer.credit_balance:.2f}) "
                f"to cover {settings.currency_symbol}{bill.total:.2f}."
            )
        customer.credit_balance = round(customer.credit_balance - bill.total, 2)
    else:
        customer.amount_due = round(customer.amount_due + bill.total, 2)

    repo.update_customer(customer)
    return customer, bill
