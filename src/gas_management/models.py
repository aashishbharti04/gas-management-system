"""Domain models for the Gas Management System."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class GasType(str, Enum):
    """Types of gas that can be sold."""

    CNG = "CNG"
    LPG = "LPG"
    BOTH = "BOTH"


@dataclass
class User:
    """An authenticated operator of the system.

    Passwords are never stored in plaintext: ``password_hash`` holds a salted
    PBKDF2 digest produced by :mod:`gas_management.auth`.
    """

    username: str
    password_hash: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Customer:
    """A gas customer account.

    Note: unlike the original prototype, payment-card numbers are deliberately
    NOT stored. ``phone`` is kept instead for contact purposes.
    """

    account_no: str
    name: str
    address: str
    phone: str = ""
    cng_litres: float = 0.0
    lpg_litres: float = 0.0
    amount_due: float = 0.0
    credit_balance: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Bill:
    """The computed result of a gas purchase."""

    gas_type: GasType
    cng_litres: float
    lpg_litres: float
    cng_amount: float
    lpg_amount: float

    @property
    def total(self) -> float:
        return round(self.cng_amount + self.lpg_amount, 2)
