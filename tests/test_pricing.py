"""Tests for billing calculations."""

from __future__ import annotations

from gas_management.config import Settings
from gas_management.models import GasType
from gas_management.pricing import compute_bill


def _settings() -> Settings:
    return Settings(cng_price=75.0, lpg_price=80.0)


def test_cng_only():
    bill = compute_bill(_settings(), GasType.CNG, cng_litres=2, lpg_litres=99)
    assert bill.cng_amount == 150.0
    assert bill.lpg_amount == 0.0  # lpg ignored for a CNG purchase
    assert bill.total == 150.0


def test_lpg_only():
    bill = compute_bill(_settings(), GasType.LPG, lpg_litres=3)
    assert bill.lpg_amount == 240.0
    assert bill.total == 240.0


def test_both():
    bill = compute_bill(_settings(), GasType.BOTH, cng_litres=1, lpg_litres=1)
    assert bill.cng_amount == 75.0
    assert bill.lpg_amount == 80.0
    assert bill.total == 155.0
