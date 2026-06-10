"""Tests for password hashing and authentication."""

from __future__ import annotations

import pytest

from gas_management.auth import authenticate, hash_password, verify_password
from gas_management.exceptions import AuthenticationError
from gas_management.models import User


def test_hash_is_salted_and_not_plaintext():
    h1 = hash_password("secret")
    h2 = hash_password("secret")
    assert "secret" not in h1
    assert h1 != h2  # different salts -> different digests
    assert h1.startswith("pbkdf2_sha256$")


def test_verify_password_roundtrip():
    h = hash_password("correct horse")
    assert verify_password("correct horse", h)
    assert not verify_password("wrong", h)


def test_verify_password_handles_malformed_hash():
    assert not verify_password("x", "not-a-valid-hash")


def test_empty_password_rejected():
    with pytest.raises(AuthenticationError):
        hash_password("")


def test_authenticate_unknown_user():
    with pytest.raises(AuthenticationError):
        authenticate("ghost", "pw", None)


def test_authenticate_success_and_failure():
    user = User(username="admin", password_hash=hash_password("pw"))
    assert authenticate("admin", "pw", user) is user
    with pytest.raises(AuthenticationError):
        authenticate("admin", "bad", user)
