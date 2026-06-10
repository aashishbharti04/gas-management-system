"""Tests for the SQLite repository and service-layer business rules."""

from __future__ import annotations

import pytest

from gas_management.exceptions import (
    CustomerNotFoundError,
    DuplicateCustomerError,
    ValidationError,
)
from gas_management.models import GasType
from gas_management.services import (
    create_customer,
    record_purchase,
    seed_default_admin,
)


def test_seed_admin_only_once(repo, settings):
    assert seed_default_admin(repo, settings) is True
    assert seed_default_admin(repo, settings) is False
    assert repo.count_users() == 1
    assert repo.get_user(settings.admin_username) is not None


def test_create_and_fetch_customer(repo):
    create_customer(repo, account_no="ACC1", name="Asha", address="12 Road", phone="123")
    fetched = repo.get_customer("ACC1")
    assert fetched is not None
    assert fetched.name == "Asha"


def test_duplicate_customer_rejected(repo):
    create_customer(repo, account_no="ACC1", name="Asha", address="12 Road")
    with pytest.raises(DuplicateCustomerError):
        create_customer(repo, account_no="ACC1", name="Other", address="9 Lane")


def test_search_and_list(repo):
    create_customer(repo, account_no="ACC1", name="Asha", address="12 Road")
    create_customer(repo, account_no="ACC2", name="Bharat", address="9 Lane")
    assert len(repo.list_customers()) == 2
    assert [c.account_no for c in repo.search_customers("Asha")] == ["ACC1"]
    assert [c.account_no for c in repo.search_customers("ACC2")] == ["ACC2"]


def test_record_purchase_adds_to_due(repo, settings):
    create_customer(repo, account_no="ACC1", name="Asha", address="12 Road")
    customer, bill = record_purchase(
        repo, settings, account_no="ACC1", gas_type=GasType.CNG, cng_litres=2
    )
    assert bill.total == 150.0
    assert customer.amount_due == 150.0
    assert customer.cng_litres == 2


def test_record_purchase_from_credit(repo, settings):
    create_customer(repo, account_no="ACC1", name="Asha", address="12 Road", credit_balance=500)
    customer, _ = record_purchase(
        repo,
        settings,
        account_no="ACC1",
        gas_type=GasType.LPG,
        lpg_litres=2,
        pay_from_credit=True,
    )
    assert customer.credit_balance == 340.0  # 500 - (80*2)
    assert customer.amount_due == 0.0


def test_record_purchase_insufficient_credit(repo, settings):
    create_customer(repo, account_no="ACC1", name="Asha", address="12 Road", credit_balance=10)
    with pytest.raises(ValidationError):
        record_purchase(
            repo,
            settings,
            account_no="ACC1",
            gas_type=GasType.CNG,
            cng_litres=5,
            pay_from_credit=True,
        )


def test_purchase_unknown_customer(repo, settings):
    with pytest.raises(CustomerNotFoundError):
        record_purchase(repo, settings, account_no="NOPE", gas_type=GasType.CNG, cng_litres=1)


def test_delete_customer(repo):
    create_customer(repo, account_no="ACC1", name="Asha", address="12 Road")
    repo.delete_customer("ACC1")
    assert repo.get_customer("ACC1") is None
    with pytest.raises(CustomerNotFoundError):
        repo.delete_customer("ACC1")
