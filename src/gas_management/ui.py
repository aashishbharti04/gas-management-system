"""Terminal user-interface helpers built on top of `rich`.

This module centralises every piece of presentation logic — colours, the banner,
menus, tables, prompts, spinners (loading states), and the professional footer —
so the CLI controller stays focused on flow rather than formatting.

Accessibility: `rich` automatically degrades to plain text when output is not a
TTY or when ``NO_COLOR`` is set, and all colours are paired with text/iconography
rather than relying on colour alone.
"""

from __future__ import annotations

import time
from collections.abc import Iterable, Sequence

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from . import __version__
from .branding import APP_NAME, CONTACT_EMAIL, SOCIAL_LINKS
from .config import Settings
from .models import Bill, Customer

__all__ = ["APP_NAME", "CONTACT_EMAIL", "SOCIAL_LINKS", "console"]

# A single theme keeps colour hierarchy consistent across the whole app.
_THEME = Theme(
    {
        "brand": "bold cyan",
        "accent": "magenta",
        "muted": "grey62",
        "success": "bold green",
        "warning": "bold yellow",
        "error": "bold red",
        "heading": "bold white",
        "value": "bright_white",
    }
)

console = Console(theme=_THEME)


# --------------------------------------------------------------------------
# Banner & footer
# --------------------------------------------------------------------------
def show_banner() -> None:
    """Render the application banner."""
    title = Text(f"⛽  {APP_NAME}", style="brand")
    subtitle = Text(f"Secure CNG / LPG billing & inventory  ·  v{__version__}", style="muted")
    body = Align.center(Text.assemble(title, "\n", subtitle))
    console.print(Panel(body, border_style="brand", padding=(1, 2)))


def show_footer() -> None:
    """Render the professional footer with contact, social and licence info."""
    lines = Text()
    lines.append("Contact  ", style="heading")
    lines.append(f"{CONTACT_EMAIL}\n", style="value")
    lines.append("Connect  ", style="heading")
    lines.append(
        "  ·  ".join(f"{name}: {url}" for name, url in SOCIAL_LINKS.items()) + "\n",
        style="muted",
    )
    lines.append(f"© {APP_NAME}. All rights reserved.\n", style="muted")
    lines.append(
        "Open source — free for educational, learning and community contributions.",
        style="accent",
    )
    console.print(
        Panel(lines, title="[heading]About[/heading]", border_style="muted", padding=(1, 2))
    )


# --------------------------------------------------------------------------
# Generic helpers (loading / success / error / empty states)
# --------------------------------------------------------------------------
def loading(message: str, *, seconds: float = 0.4) -> None:
    """Show a transient spinner — a lightweight 'loading state'."""
    with console.status(f"[muted]{message}[/muted]", spinner="dots"):
        time.sleep(max(0.0, seconds))


def success(message: str) -> None:
    console.print(f"[success]✓[/success] {message}")


def warn(message: str) -> None:
    console.print(f"[warning]![/warning] {message}")


def error(message: str) -> None:
    console.print(f"[error]✗ {message}[/error]")


def info(message: str) -> None:
    console.print(f"[muted]›[/muted] {message}")


def empty_state(message: str) -> None:
    """A friendly placeholder shown when there is no data to display."""
    console.print(
        Panel(
            Align.center(Text(f"📭  {message}", style="muted")),
            border_style="muted",
            padding=(1, 2),
        )
    )


# --------------------------------------------------------------------------
# Prompts
# --------------------------------------------------------------------------
def ask(prompt: str, *, default: str | None = None, password: bool = False) -> str:
    return Prompt.ask(f"[heading]{prompt}[/heading]", default=default, password=password)


def ask_choice(prompt: str, choices: Sequence[str], *, default: str | None = None) -> str:
    return Prompt.ask(f"[heading]{prompt}[/heading]", choices=list(choices), default=default)


def confirm(prompt: str, *, default: bool = False) -> bool:
    return Confirm.ask(f"[heading]{prompt}[/heading]", default=default)


# --------------------------------------------------------------------------
# Menu
# --------------------------------------------------------------------------
def show_menu(items: Iterable[tuple[str, str]]) -> None:
    """Render the main menu from ``(key, label)`` pairs."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(justify="right", style="accent", no_wrap=True)
    table.add_column(style="value")
    for key, label in items:
        table.add_row(key, label)
    console.print(Panel(table, title="[heading]Menu[/heading]", border_style="brand"))


# --------------------------------------------------------------------------
# Domain rendering
# --------------------------------------------------------------------------
def _money(settings: Settings, amount: float) -> str:
    return f"{settings.currency_symbol}{amount:,.2f}"


def render_customer(settings: Settings, customer: Customer) -> None:
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="heading", no_wrap=True)
    table.add_column(style="value")
    table.add_row("Account No", customer.account_no)
    table.add_row("Name", customer.name)
    table.add_row("Address", customer.address)
    table.add_row("Phone", customer.phone or "—")
    table.add_row("CNG (litres)", f"{customer.cng_litres:g}")
    table.add_row("LPG (litres)", f"{customer.lpg_litres:g}")
    table.add_row("Amount Due", _money(settings, customer.amount_due))
    table.add_row("Credit Balance", _money(settings, customer.credit_balance))
    console.print(Panel(table, title=f"[heading]{customer.name}[/heading]", border_style="brand"))


def render_customers_table(settings: Settings, customers: Sequence[Customer]) -> None:
    if not customers:
        empty_state("No customers found.")
        return
    table = Table(border_style="muted", header_style="heading", row_styles=["", "muted"])
    table.add_column("Account", no_wrap=True)
    table.add_column("Name")
    table.add_column("Phone")
    table.add_column("CNG (L)", justify="right")
    table.add_column("LPG (L)", justify="right")
    table.add_column("Due", justify="right")
    table.add_column("Credit", justify="right")
    for c in customers:
        table.add_row(
            c.account_no,
            c.name,
            c.phone or "—",
            f"{c.cng_litres:g}",
            f"{c.lpg_litres:g}",
            _money(settings, c.amount_due),
            _money(settings, c.credit_balance),
        )
    console.print(table)
    info(f"{len(customers)} customer(s).")


def render_bill(settings: Settings, customer: Customer, bill: Bill) -> None:
    table = Table(show_header=True, header_style="heading", border_style="brand")
    table.add_column("Item")
    table.add_column("Litres", justify="right")
    table.add_column("Rate", justify="right")
    table.add_column("Amount", justify="right")
    if bill.cng_litres:
        table.add_row(
            "CNG",
            f"{bill.cng_litres:g}",
            _money(settings, settings.cng_price),
            _money(settings, bill.cng_amount),
        )
    if bill.lpg_litres:
        table.add_row(
            "LPG",
            f"{bill.lpg_litres:g}",
            _money(settings, settings.lpg_price),
            _money(settings, bill.lpg_amount),
        )
    table.add_section()
    table.add_row(
        "[heading]Total[/heading]", "", "", f"[success]{_money(settings, bill.total)}[/success]"
    )
    console.print(
        Panel(table, title=f"[heading]Invoice · {customer.name}[/heading]", border_style="brand")
    )
