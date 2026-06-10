"""Security helpers for the web dashboard: sessions, CSRF, and auth guards.

- Session cookies are signed (Starlette ``SessionMiddleware``) and marked HttpOnly
  + SameSite=Lax; ``Secure`` is enabled when ``web_cookie_secure`` is set.
- A per-session CSRF token protects every state-changing (POST) request using the
  synchroniser-token pattern with a constant-time comparison.
- ``RedirectToLogin`` lets dependencies short-circuit unauthenticated requests.
"""

from __future__ import annotations

import hmac
import secrets

from starlette.requests import Request

SESSION_USER_KEY = "user"
SESSION_CSRF_KEY = "csrf_token"


class RedirectToLogin(Exception):
    """Raised by guards to send an unauthenticated user to the login page."""

    def __init__(self, next_url: str = "/") -> None:
        self.next_url = next_url
        super().__init__("authentication required")


class CSRFError(Exception):
    """Raised when a submitted CSRF token is missing or invalid."""


def current_user(request: Request) -> str | None:
    """Return the logged-in username from the session, if any."""
    return request.session.get(SESSION_USER_KEY)


def require_user(request: Request) -> str:
    """FastAPI dependency: ensure a user is logged in or redirect to login."""
    user = current_user(request)
    if not user:
        raise RedirectToLogin(next_url=request.url.path)
    return user


def login_session(request: Request, username: str) -> None:
    """Mark the session as authenticated and rotate the CSRF token."""
    request.session[SESSION_USER_KEY] = username
    request.session[SESSION_CSRF_KEY] = secrets.token_urlsafe(32)


def logout_session(request: Request) -> None:
    request.session.clear()


def get_csrf_token(request: Request) -> str:
    """Return the session CSRF token, creating one if necessary."""
    token = request.session.get(SESSION_CSRF_KEY)
    if not token:
        token = secrets.token_urlsafe(32)
        request.session[SESSION_CSRF_KEY] = token
    return token


def verify_csrf(request: Request, submitted: str | None) -> None:
    """Validate a submitted CSRF token against the session token."""
    expected = request.session.get(SESSION_CSRF_KEY)
    if not expected or not submitted or not hmac.compare_digest(expected, submitted):
        raise CSRFError("Invalid or missing CSRF token. Please retry.")
