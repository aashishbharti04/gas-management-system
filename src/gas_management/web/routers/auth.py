"""Authentication routes: login and logout."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Form
from starlette.requests import Request
from starlette.responses import RedirectResponse

from ...db import Repository
from ...exceptions import AuthenticationError
from ...services import login
from ..dependencies import get_repo, render
from ..security import current_user, login_session, logout_session, verify_csrf

router = APIRouter()


def _safe_next(raw: str | None) -> str:
    """Only allow same-site relative redirects (prevents open redirects)."""
    if raw and raw.startswith("/") and not raw.startswith("//"):
        return raw
    return "/"


@router.get("/login")
def login_form(request: Request, next: str = "/"):
    if current_user(request):
        return RedirectResponse("/", status_code=303)
    return render(request, "login.html", next_url=_safe_next(next))


@router.post("/login")
def login_submit(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    csrf_token: Annotated[str, Form()] = "",
    next: Annotated[str, Form()] = "/",
    repo: Repository = Depends(get_repo),
):
    verify_csrf(request, csrf_token)
    try:
        user = login(repo, username.strip(), password)
    except AuthenticationError:
        return render(
            request,
            "login.html",
            error="Invalid username or password.",
            next_url=_safe_next(next),
            username=username,
            status_code=401,
        )
    login_session(request, user.username)
    return RedirectResponse(_safe_next(next), status_code=303)


@router.post("/logout")
def logout(request: Request, csrf_token: Annotated[str, Form()] = ""):
    verify_csrf(request, csrf_token)
    logout_session(request)
    return RedirectResponse("/login", status_code=303)
