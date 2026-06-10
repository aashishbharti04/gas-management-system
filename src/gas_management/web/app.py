"""FastAPI application factory for the Gas Management System dashboard."""

from __future__ import annotations

import logging
import secrets
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.staticfiles import StaticFiles

from .. import __version__
from ..config import Settings
from ..services import seed_default_admin
from .dependencies import get_settings, render
from .routers import auth, billing, customers, dashboard
from .security import CSRFError, RedirectToLogin

logger = logging.getLogger("gas_management.web")

_STATIC_DIR = Path(__file__).parent / "static"

# Content-Security-Policy: only same-origin assets; no inline scripts/styles.
_CSP = (
    "default-src 'self'; img-src 'self' data:; style-src 'self'; "
    "script-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
)
_SECURITY_HEADERS = {
    "Content-Security-Policy": _CSP,
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
}


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = settings or get_settings()

    secret = settings.web_secret_key or secrets.token_urlsafe(48)
    if not settings.web_secret_key:
        logger.warning(
            "GMS_WEB_SECRET_KEY is not set; using an ephemeral key. "
            "Sessions will be invalidated on restart. Set it for production."
        )

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        # Seed the default admin once at startup so first-time login works.
        from ..db import create_repository

        with create_repository(settings) as repo:
            if seed_default_admin(repo, settings):
                logger.warning(
                    "Seeded default admin '%s'. Change GMS_ADMIN_USERNAME / "
                    "GMS_ADMIN_PASSWORD for production.",
                    settings.admin_username,
                )
        yield

    app = FastAPI(
        title="Gas Management System",
        version=__version__,
        description="Web dashboard for managing gas customers, billing and inventory.",
        docs_url=None,  # disable interactive API docs for this server-rendered app
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )

    app.add_middleware(
        SessionMiddleware,
        secret_key=secret,
        same_site="lax",
        https_only=settings.web_cookie_secure,
        session_cookie="gms_session",
    )

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response: Response = await call_next(request)
        for header, value in _SECURITY_HEADERS.items():
            response.headers.setdefault(header, value)
        return response

    # --- exception handlers -------------------------------------------------
    @app.exception_handler(RedirectToLogin)
    async def _redirect_to_login(request: Request, exc: RedirectToLogin):
        target = "/login"
        if exc.next_url and exc.next_url != "/":
            target = f"/login?next={exc.next_url}"
        return RedirectResponse(target, status_code=303)

    @app.exception_handler(CSRFError)
    async def _csrf_error(request: Request, exc: CSRFError):
        return render(request, "error.html", message=str(exc), status_code=400)

    @app.exception_handler(404)
    async def _not_found(request: Request, exc: object):
        return render(
            request,
            "not_found.html",
            message="The page you requested could not be found.",
            status_code=404,
        )

    # --- routes -------------------------------------------------------------
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

    @app.get("/healthz", include_in_schema=False)
    def healthz():
        return {"status": "ok", "version": __version__}

    app.include_router(auth.router)
    app.include_router(dashboard.router)
    app.include_router(customers.router)
    app.include_router(billing.router)

    return app
