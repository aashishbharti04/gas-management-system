"""Authentication helpers: secure password hashing and verification.

Passwords are hashed with PBKDF2-HMAC-SHA256 using a per-password random salt.
The stored format is ``pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>`` so the
parameters travel with the digest and can be upgraded over time.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets

from .exceptions import AuthenticationError
from .models import User

_ALGORITHM = "pbkdf2_sha256"
_ITERATIONS = 240_000
_SALT_BYTES = 16


def hash_password(password: str, *, iterations: int = _ITERATIONS) -> str:
    """Return a salted PBKDF2 hash string for ``password``."""
    if not password:
        raise AuthenticationError("Password must not be empty.")
    salt = secrets.token_bytes(_SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"{_ALGORITHM}${iterations}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Return ``True`` if ``password`` matches the ``stored`` hash string.

    Uses a constant-time comparison to avoid timing side channels.
    """
    try:
        algorithm, iterations_s, salt_hex, hash_hex = stored.split("$")
        if algorithm != _ALGORITHM:
            return False
        iterations = int(iterations_s)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
    except (ValueError, AttributeError):
        return False
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(candidate, expected)


def authenticate(username: str, password: str, user: User | None) -> User:
    """Validate credentials against a (possibly missing) user record.

    A dummy hash check is performed for unknown users so that response time does
    not reveal whether a username exists.
    """
    if user is None:
        # Spend comparable time to a real verification to mask user enumeration.
        verify_password(password, hash_password("__nonexistent__"))
        raise AuthenticationError("Invalid username or password.")
    if not verify_password(password, user.password_hash):
        raise AuthenticationError("Invalid username or password.")
    return user
