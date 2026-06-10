"""Customer management routes: list, create, view, delete."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Form
from starlette.requests import Request
from starlette.responses import RedirectResponse

from ...db import Repository
from ...exceptions import DuplicateCustomerError, ValidationError
from ...services import create_customer
from ...validators import (
    validate_account_no,
    validate_address,
    validate_amount,
    validate_name,
    validate_phone,
)
from ..dependencies import flash, get_repo, render
from ..security import require_user, verify_csrf

router = APIRouter()


@router.get("/customers")
def list_customers(
    request: Request,
    q: str = "",
    partial: int = 0,
    _user: str = Depends(require_user),
    repo: Repository = Depends(get_repo),
):
    term = q.strip()
    customers = repo.search_customers(term) if term else repo.list_customers()
    # `partial=1` returns only the results table (used by the live-search fetch),
    # so the page can show skeleton rows then swap in real data without a reload.
    template = "_customers_table.html" if partial else "customers_list.html"
    return render(
        request,
        template,
        customers=customers,
        query=term,
        active="customers",
    )


@router.get("/customers/new")
def new_customer_form(request: Request, _user: str = Depends(require_user)):
    return render(request, "customer_new.html", active="customers", form={})


@router.post("/customers")
def create_customer_submit(
    request: Request,
    account_no: Annotated[str, Form()],
    name: Annotated[str, Form()],
    address: Annotated[str, Form()],
    phone: Annotated[str, Form()] = "",
    credit_balance: Annotated[str, Form()] = "0",
    csrf_token: Annotated[str, Form()] = "",
    _user: str = Depends(require_user),
    repo: Repository = Depends(get_repo),
):
    verify_csrf(request, csrf_token)
    form = {
        "account_no": account_no,
        "name": name,
        "address": address,
        "phone": phone,
        "credit_balance": credit_balance,
    }
    try:
        clean = {
            "account_no": validate_account_no(account_no),
            "name": validate_name(name),
            "address": validate_address(address),
            "phone": validate_phone(phone),
            "credit_balance": validate_amount(credit_balance, field="Credit balance"),
        }
        create_customer(repo, **clean)
    except (ValidationError, DuplicateCustomerError) as exc:
        return render(
            request,
            "customer_new.html",
            active="customers",
            form=form,
            error=str(exc),
            status_code=400,
        )
    flash(request, f"Customer '{clean['name']}' created.", "success")
    return RedirectResponse(f"/customers/{clean['account_no']}", status_code=303)


@router.get("/customers/{account_no}")
def view_customer(
    request: Request,
    account_no: str,
    _user: str = Depends(require_user),
    repo: Repository = Depends(get_repo),
):
    customer = repo.get_customer(account_no)
    if customer is None:
        return render(
            request,
            "not_found.html",
            active="customers",
            message=f"No customer with account '{account_no}'.",
            status_code=404,
        )
    return render(request, "customer_detail.html", customer=customer, active="customers")


@router.post("/customers/{account_no}/delete")
def delete_customer_submit(
    request: Request,
    account_no: str,
    csrf_token: Annotated[str, Form()] = "",
    _user: str = Depends(require_user),
    repo: Repository = Depends(get_repo),
):
    verify_csrf(request, csrf_token)
    customer = repo.get_customer(account_no)
    if customer is None:
        flash(request, f"No customer with account '{account_no}'.", "error")
        return RedirectResponse("/customers", status_code=303)
    repo.delete_customer(account_no)
    flash(request, f"Customer '{customer.name}' deleted.", "success")
    return RedirectResponse("/customers", status_code=303)
