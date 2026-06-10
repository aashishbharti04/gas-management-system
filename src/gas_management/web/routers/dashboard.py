"""Dashboard route: at-a-glance statistics."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from starlette.requests import Request

from ...db import Repository
from ..dependencies import get_repo, render
from ..security import require_user

router = APIRouter()


@router.get("/")
def dashboard(
    request: Request,
    _user: str = Depends(require_user),
    repo: Repository = Depends(get_repo),
):
    customers = repo.list_customers()
    stats = {
        "customer_count": len(customers),
        "total_due": round(sum(c.amount_due for c in customers), 2),
        "total_credit": round(sum(c.credit_balance for c in customers), 2),
        "total_cng": round(sum(c.cng_litres for c in customers), 2),
        "total_lpg": round(sum(c.lpg_litres for c in customers), 2),
    }
    # Customers with the highest outstanding dues, for a quick "attention" list.
    top_due = sorted(
        (c for c in customers if c.amount_due > 0),
        key=lambda c: c.amount_due,
        reverse=True,
    )[:5]
    recent = sorted(customers, key=lambda c: c.created_at, reverse=True)[:5]
    return render(
        request,
        "dashboard.html",
        stats=stats,
        top_due=top_due,
        recent=recent,
        active="dashboard",
    )
