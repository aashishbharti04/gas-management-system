"""End-to-end tests for the FastAPI web dashboard using Starlette's TestClient.

Skipped automatically if the optional web dependencies are not installed.
"""

from __future__ import annotations

import re

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("multipart")
from fastapi.testclient import TestClient  # noqa: E402

from gas_management.config import Settings  # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("GMS_SQLITE_PATH", str(tmp_path / "web.db"))
    monkeypatch.setenv("GMS_WEB_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("GMS_ADMIN_USERNAME", "admin")
    monkeypatch.setenv("GMS_ADMIN_PASSWORD", "admin123")

    from gas_management.web import app as app_module
    from gas_management.web import dependencies

    dependencies.get_settings.cache_clear()
    application = app_module.create_app(Settings.from_env())
    with TestClient(application) as c:
        yield c
    dependencies.get_settings.cache_clear()


def _csrf(client: TestClient, path: str) -> str:
    html = client.get(path).text
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, f"no CSRF token found on {path}"
    return match.group(1)


def _login(client: TestClient) -> None:
    token = _csrf(client, "/login")
    resp = client.post(
        "/login",
        data={"username": "admin", "password": "admin123", "csrf_token": token},
    )
    assert resp.status_code == 200
    assert "Dashboard" in resp.text


def test_login_page_renders(client):
    resp = client.get("/login")
    assert resp.status_code == 200
    assert "Sign in" in resp.text


def test_dashboard_requires_authentication(client):
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 303
    assert resp.headers["location"].startswith("/login")


def test_healthz(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_bad_login_rejected(client):
    token = _csrf(client, "/login")
    resp = client.post(
        "/login",
        data={"username": "admin", "password": "wrong", "csrf_token": token},
    )
    assert resp.status_code == 401
    assert "Invalid username or password" in resp.text


def test_login_requires_csrf(client):
    resp = client.post(
        "/login",
        data={"username": "admin", "password": "admin123", "csrf_token": "bogus"},
    )
    assert resp.status_code == 400


def test_full_customer_and_billing_flow(client):
    _login(client)

    # Create a customer.
    token = _csrf(client, "/customers/new")
    resp = client.post(
        "/customers",
        data={
            "account_no": "ACC100",
            "name": "Aasha Devi",
            "address": "12 Gas Lane",
            "phone": "9999999999",
            "credit_balance": "500",
            "csrf_token": token,
        },
    )
    assert resp.status_code == 200
    assert "Aasha Devi" in resp.text

    # It appears in the list and in partial search.
    assert "ACC100" in client.get("/customers").text
    assert "Aasha Devi" in client.get("/customers?partial=1&q=Aasha").text

    # Record a CNG purchase (2 L * 75 = 150).
    token = _csrf(client, "/billing")
    resp = client.post(
        "/billing",
        data={
            "account_no": "ACC100",
            "gas_type": "CNG",
            "cng_litres": "2",
            "csrf_token": token,
        },
    )
    assert resp.status_code == 200
    assert "150.00" in resp.text

    # Duplicate account is rejected.
    token = _csrf(client, "/customers/new")
    dup = client.post(
        "/customers",
        data={
            "account_no": "ACC100",
            "name": "Other",
            "address": "9 Lane",
            "csrf_token": token,
        },
    )
    assert dup.status_code == 400
    assert "already exists" in dup.text


def test_logout(client):
    _login(client)
    token = _csrf(client, "/customers/new")
    resp = client.post("/logout", data={"csrf_token": token}, follow_redirects=False)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/login"
    # After logout, protected pages redirect again.
    assert client.get("/", follow_redirects=False).status_code == 303
