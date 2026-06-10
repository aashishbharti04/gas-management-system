"""Billing routes: record a gas purchase and show the generated invoice."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Form
from starlette.requests import Request

from ...config import Settings
from ...db import Repository
from ...exceptions import CustomerNotFoundError, ValidationError
from ...models import GasType
from ...services import record_purchase
from ...validators import validate_account_no, validate_litres
from ..dependencies import get_repo, get_settings, render
from ..security import require_user, verify_csrf

router = APIRouter()


@router.get("/billing")
def billing_form(
    request: Request,
    account_no: str = "",
    _user: str = Depends(require_user),
):
    return render(
        request,
        "billing.html",
        active="billing",
        form={"account_no": account_no.strip()},
    )


@router.post("/billing")
def billing_submit(
    request: Request,
    account_no: Annotated[str, Form()],
    gas_type: Annotated[str, Form()],
    cng_litres: Annotated[str, Form()] = "0",
    lpg_litres: Annotated[str, Form()] = "0",
    pay_from_credit: Annotated[str, Form()] = "",
    csrf_token: Annotated[str, Form()] = "",
    _user: str = Depends(require_user),
    repo: Repository = Depends(get_repo),
    settings: Settings = Depends(get_settings),
):
    verify_csrf(request, csrf_token)
    form = {
        "account_no": account_no,
        "gas_type": gas_type,
        "cng_litres": cng_litres,
        "lpg_litres": lpg_litres,
        "pay_from_credit": bool(pay_from_credit),
    }

    def _error(message: str):
        return render(
            request, "billing.html", active="billing", form=form, error=message, status_code=400
        )

    try:
        gtype = GasType(gas_type.upper())
    except ValueError:
        return _error("Please choose a valid gas type.")

    try:
        acc = validate_account_no(account_no)
        cng = validate_litres(cng_litres) if gtype in (GasType.CNG, GasType.BOTH) else 0.0
        lpg = validate_litres(lpg_litres) if gtype in (GasType.LPG, GasType.BOTH) else 0.0
        customer, bill = record_purchase(
            repo,
            settings,
            account_no=acc,
            gas_type=gtype,
            cng_litres=cng,
            lpg_litres=lpg,
            pay_from_credit=bool(pay_from_credit),
        )
    except CustomerNotFoundError as exc:
        return _error(str(exc))
    except ValidationError as exc:
        return _error(str(exc))

    return render(
        request,
        "billing_result.html",
        active="billing",
        customer=customer,
        bill=bill,
    )
