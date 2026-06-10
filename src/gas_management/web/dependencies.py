"""Shared FastAPI dependencies and the Jinja2 templating helper."""

from __future__ import annotations

from collections.abc import Iterator
from functools import lru_cache
from pathlib import Path

from starlette.requests import Request
from starlette.templating import Jinja2Templates

from .. import __version__
from ..branding import (
    APP_NAME,
    CONTACT_EMAIL,
    COPYRIGHT,
    OPEN_SOURCE_NOTICE,
    SOCIAL_LINKS,
    TAGLINE,
)
from ..config import Settings
from ..db import Repository, create_repository
from .security import current_user, get_csrf_token

_TEMPLATES_DIR = Path(__file__).parent / "templates"

templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings.from_env()


def get_repo() -> Iterator[Repository]:
    """Provide a request-scoped repository and close it afterwards.

    A fresh connection per request keeps the SQLite backend thread-safe under the
    threadpool FastAPI uses for synchronous endpoints.
    """
    repo = create_repository(get_settings())
    repo.initialize()
    try:
        yield repo
    finally:
        repo.close()


def render(request: Request, template: str, *, status_code: int = 200, **context: object):
    """Render a template with the common context every page needs."""
    settings = get_settings()
    flashes = request.session.pop("_flashes", [])
    base = {
        "request": request,
        "app_name": APP_NAME,
        "tagline": TAGLINE,
        "version": __version__,
        "settings": settings,
        "currency": settings.currency_symbol,
        "current_user": current_user(request),
        "csrf_token": get_csrf_token(request),
        "flashes": flashes,
        "contact_email": CONTACT_EMAIL,
        "social_links": SOCIAL_LINKS,
        "copyright": COPYRIGHT,
        "open_source_notice": OPEN_SOURCE_NOTICE,
    }
    base.update(context)
    return templates.TemplateResponse(request, template, base, status_code=status_code)


def flash(request: Request, message: str, category: str = "info") -> None:
    """Queue a one-time flash message shown on the next rendered page."""
    request.session.setdefault("_flashes", []).append({"message": message, "category": category})
