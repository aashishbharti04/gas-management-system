"""Storage layer for the Gas Management System.

Exposes a backend-agnostic :class:`Repository` interface plus a factory that
returns a concrete SQLite or MySQL implementation based on configuration.
"""

from __future__ import annotations

from .base import Repository
from .factory import create_repository

__all__ = ["Repository", "create_repository"]
