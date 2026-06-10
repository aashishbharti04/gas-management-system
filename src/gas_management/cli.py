"""Command-line controller — wires the UI to the services and storage layers.

This module owns the interactive flow only; all business rules live in
:mod:`gas_management.services` and all persistence in :mod:`gas_management.db`.
"""

from __future__ import annotations

import contextlib
import sys

from . import ui
from .config import Settings, load_dotenv
from .db import create_repository
from .exceptions import (
    AuthenticationError,
    GasManagementError,
    ValidationError,
)
from .models import GasType
from .services import (
    create_customer,
    login,
    record_purchase,
    seed_default_admin,
)
from .validators import (
    validate_account_no,
    validate_address,
    validate_amount,
    validate_litres,
    validate_name,
    validate_phone,
)

MAX_LOGIN_ATTEMPTS = 3


def _configure_stdio() -> None:
    """Force UTF-8 console I/O so rich glyphs render on every platform.

    Windows' legacy code pages (e.g. cp1252) cannot encode characters such as
    ``⛽``; reconfiguring with ``errors='replace'`` guarantees we never crash on
    output regardless of the host terminal.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            # Platform-dependent; safe to ignore if the stream can't be reconfigured.
            with contextlib.suppress(ValueError, OSError):
                reconfigure(encoding="utf-8", errors="replace")


_MENU = [
    ("1", "Create customer account"),
    ("2", "Record gas purchase / generate bill"),
    ("3", "View a customer's details"),
    ("4", "List all customers"),
    ("5", "Search customers"),
    ("6", "Delete a customer"),
    ("0", "Log out & exit"),
]


def _prompt_valid(label: str, validator, **kwargs):
    """Prompt repeatedly until the validator accepts the input."""
    while True:
        raw = ui.ask(label, **kwargs)
        try:
            return validator(raw)
        except ValidationError as exc:
            ui.error(str(exc))


def _do_login(repo) -> bool:
    for attempt in range(1, MAX_LOGIN_ATTEMPTS + 1):
        username = ui.ask("Username")
        password = ui.ask("Password", password=True)
        ui.loading("Authenticating")
        try:
            user = login(repo, username, password)
        except AuthenticationError as exc:
            remaining = MAX_LOGIN_ATTEMPTS - attempt
            ui.error(f"{exc} ({remaining} attempt(s) left)" if remaining else str(exc))
            continue
        ui.success(f"Welcome, {user.username}!")
        return True
    ui.error("Too many failed attempts. Access denied.")
    return False


def _action_create_customer(repo, settings: Settings) -> None:
    ui.console.rule("[heading]Create customer account[/heading]")
    account_no = _prompt_valid("Account number", validate_account_no)
    name = _prompt_valid("Customer name", validate_name)
    address = _prompt_valid("Address", validate_address)
    phone = _prompt_valid("Phone (optional)", validate_phone, default="")
    credit = _prompt_valid("Opening credit balance", validate_amount, default="0")
    ui.loading("Saving account")
    customer = create_customer(
        repo,
        account_no=account_no,
        name=name,
        address=address,
        phone=phone,
        credit_balance=credit,
    )
    ui.success(f"Account {customer.account_no} created for {customer.name}.")
    ui.render_customer(settings, customer)


def _action_record_purchase(repo, settings: Settings) -> None:
    ui.console.rule("[heading]Record gas purchase[/heading]")
    account_no = _prompt_valid("Customer account number", validate_account_no)
    ui.console.print(
        f"  [accent]1[/accent] CNG  ({settings.currency_symbol}{settings.cng_price:g}/L)\n"
        f"  [accent]2[/accent] LPG  ({settings.currency_symbol}{settings.lpg_price:g}/L)\n"
        f"  [accent]3[/accent] Both"
    )
    choice = ui.ask_choice("Select gas type", ["1", "2", "3"])
    gas_type = {"1": GasType.CNG, "2": GasType.LPG, "3": GasType.BOTH}[choice]

    cng_litres = lpg_litres = 0.0
    if gas_type in (GasType.CNG, GasType.BOTH):
        cng_litres = _prompt_valid("CNG litres", validate_litres)
    if gas_type in (GasType.LPG, GasType.BOTH):
        lpg_litres = _prompt_valid("LPG litres", validate_litres)

    pay_from_credit = ui.confirm("Pay using the customer's credit balance?")
    ui.loading("Generating invoice")
    customer, bill = record_purchase(
        repo,
        settings,
        account_no=account_no,
        gas_type=gas_type,
        cng_litres=cng_litres,
        lpg_litres=lpg_litres,
        pay_from_credit=pay_from_credit,
    )
    ui.render_bill(settings, customer, bill)
    ui.success("Purchase recorded and balances updated.")
    ui.render_customer(settings, customer)


def _action_view_customer(repo, settings: Settings) -> None:
    ui.console.rule("[heading]Customer details[/heading]")
    account_no = _prompt_valid("Account number", validate_account_no)
    ui.loading("Fetching record")
    customer = repo.get_customer(account_no)
    if customer is None:
        ui.empty_state(f"No customer found with account {account_no}.")
        return
    ui.render_customer(settings, customer)


def _action_list_customers(repo, settings: Settings) -> None:
    ui.console.rule("[heading]All customers[/heading]")
    ui.loading("Loading customers")
    ui.render_customers_table(settings, repo.list_customers())


def _action_search_customers(repo, settings: Settings) -> None:
    ui.console.rule("[heading]Search customers[/heading]")
    term = ui.ask("Search by name or account number")
    ui.loading("Searching")
    ui.render_customers_table(settings, repo.search_customers(term.strip()))


def _action_delete_customer(repo, settings: Settings) -> None:
    ui.console.rule("[heading]Delete customer[/heading]")
    account_no = _prompt_valid("Account number", validate_account_no)
    customer = repo.get_customer(account_no)
    if customer is None:
        ui.empty_state(f"No customer found with account {account_no}.")
        return
    ui.render_customer(settings, customer)
    if not ui.confirm(f"Permanently delete {customer.name}?", default=False):
        ui.info("Cancelled.")
        return
    ui.loading("Deleting")
    repo.delete_customer(account_no)
    ui.success(f"Customer {account_no} deleted.")


_ACTIONS = {
    "1": _action_create_customer,
    "2": _action_record_purchase,
    "3": _action_view_customer,
    "4": _action_list_customers,
    "5": _action_search_customers,
    "6": _action_delete_customer,
}


def _main_loop(repo, settings: Settings) -> None:
    while True:
        ui.show_menu(_MENU)
        choice = ui.ask_choice("Choose an option", [k for k, _ in _MENU])
        if choice == "0":
            ui.info("Logging out…")
            break
        action = _ACTIONS.get(choice)
        if action is None:  # pragma: no cover - guarded by ask_choice
            ui.warn("Invalid option.")
            continue
        try:
            action(repo, settings)
        except GasManagementError as exc:
            ui.error(str(exc))


def run() -> int:
    """Application entry point. Returns a process exit code."""
    _configure_stdio()
    load_dotenv()
    settings = Settings.from_env()

    ui.show_banner()
    try:
        with create_repository(settings) as repo:
            if seed_default_admin(repo, settings):
                ui.warn(
                    f"Seeded default admin '{settings.admin_username}'. "
                    "Set GMS_ADMIN_USERNAME / GMS_ADMIN_PASSWORD and change it."
                )
            if not _do_login(repo):
                return 1
            _main_loop(repo, settings)
    except KeyboardInterrupt:
        ui.console.print()
        ui.info("Interrupted. Goodbye!")
        return 130
    except GasManagementError as exc:
        ui.error(str(exc))
        return 1
    finally:
        ui.show_footer()
    return 0


def main() -> None:
    """Console-script wrapper used by the ``gas-management`` entry point."""
    sys.exit(run())


if __name__ == "__main__":
    main()
