"""Tests for input validators."""

from __future__ import annotations

import pytest

from gas_management.exceptions import ValidationError
from gas_management.validators import (
    validate_account_no,
    validate_address,
    validate_amount,
    validate_litres,
    validate_name,
    validate_phone,
)


@pytest.mark.parametrize("value", ["Aashish", "Mary-Jane", "O'Neil", "A B"])
def test_valid_names(value):
    assert validate_name(value) == value.strip()


@pytest.mark.parametrize("value", ["", "A", "John123", "@@@"])
def test_invalid_names(value):
    with pytest.raises(ValidationError):
        validate_name(value)


@pytest.mark.parametrize("value", ["ACC001", "12345", "ab-_99"])
def test_valid_account_numbers(value):
    assert validate_account_no(value) == value


@pytest.mark.parametrize("value", ["ab", "has space", "toolong" * 5])
def test_invalid_account_numbers(value):
    with pytest.raises(ValidationError):
        validate_account_no(value)


def test_address_bounds():
    assert validate_address("12 Main Street")
    with pytest.raises(ValidationError):
        validate_address("ab")


def test_phone_optional_and_validated():
    assert validate_phone("") == ""
    assert validate_phone("+91 99999-99999")
    with pytest.raises(ValidationError):
        validate_phone("call-me")


def test_amount_validation():
    assert validate_amount("10.5") == 10.5
    assert validate_amount(0) == 0.0
    with pytest.raises(ValidationError):
        validate_amount("-1")
    with pytest.raises(ValidationError):
        validate_amount("abc")


def test_litres_must_be_positive():
    assert validate_litres("3") == 3.0
    with pytest.raises(ValidationError):
        validate_litres("0")
    with pytest.raises(ValidationError):
        validate_litres("-2")
