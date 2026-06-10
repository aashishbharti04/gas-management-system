"""Billing calculations for gas purchases."""

from __future__ import annotations

from .config import Settings
from .models import Bill, GasType


def compute_bill(
    settings: Settings,
    gas_type: GasType,
    *,
    cng_litres: float = 0.0,
    lpg_litres: float = 0.0,
) -> Bill:
    """Compute a :class:`Bill` for the requested gas purchase.

    Quantities for gas types not included in ``gas_type`` are ignored so callers
    can pass both and let the selection decide what is charged.
    """
    cng_qty = cng_litres if gas_type in (GasType.CNG, GasType.BOTH) else 0.0
    lpg_qty = lpg_litres if gas_type in (GasType.LPG, GasType.BOTH) else 0.0

    cng_amount = round(cng_qty * settings.cng_price, 2)
    lpg_amount = round(lpg_qty * settings.lpg_price, 2)

    return Bill(
        gas_type=gas_type,
        cng_litres=cng_qty,
        lpg_litres=lpg_qty,
        cng_amount=cng_amount,
        lpg_amount=lpg_amount,
    )
