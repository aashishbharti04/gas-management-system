"""Input validation helpers.

These functions normalise and validate user input *before* it reaches the
storage layer, raising :class:`ValidationError` with a friendly message on bad
input. All database access uses parameterised queries, so this layer is about
data quality and UX rather than injection defence.
"""

from __future__ import annotations

import re

from .exceptions import ValidationError

_ACCOUNT_RE = re.compile(r"^[A-Za-z0-9_-]{3,20}$")
_PHONE_RE = re.compile(r"^[0-9+\-\s]{0,20}$")
_NAME_RE = re.compile(r"^[A-Za-z .'-]{2,40}$")


def validate_name(value: str) -> str:
    name = value.strip()
    if not _NAME_RE.match(name):
        raise ValidationError("Name must be 2-40 letters (spaces, ', - and . allowed).")
    return name


def validate_account_no(value: str) -> str:
    account = value.strip()
    if not _ACCOUNT_RE.match(account):
        raise ValidationError(
            "Account number must be 3-20 characters (letters, digits, '-' or '_')."
        )
    return account


def validate_address(value: str) -> str:
    address = value.strip()
    if not 3 <= len(address) <= 120:
        raise ValidationError("Address must be between 3 and 120 characters.")
    return address


def validate_phone(value: str) -> str:
    phone = value.strip()
    if phone and not _PHONE_RE.match(phone):
        raise ValidationError("Phone may contain only digits, spaces, '+' and '-'.")
    return phone


def validate_amount(value: str | float, *, field: str = "Amount") -> float:
    """Validate a non-negative monetary amount."""
    try:
        amount = float(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{field} must be a number.") from exc
    if amount < 0:
        raise ValidationError(f"{field} must not be negative.")
    return round(amount, 2)


def validate_litres(value: str | float) -> float:
    """Validate a strictly positive quantity of litres."""
    try:
        litres = float(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError("Quantity must be a number.") from exc
    if litres <= 0:
        raise ValidationError("Quantity must be greater than zero.")
    return round(litres, 2)
