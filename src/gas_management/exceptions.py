"""Custom exception hierarchy for the Gas Management System.

Using domain-specific exceptions keeps error handling explicit and avoids
leaking low-level database or driver errors to the user interface.
"""

from __future__ import annotations


class GasManagementError(Exception):
    """Base class for all application-specific errors."""


class ConfigurationError(GasManagementError):
    """Raised when the application is misconfigured (e.g. bad env values)."""


class ValidationError(GasManagementError):
    """Raised when user-supplied input fails validation."""


class AuthenticationError(GasManagementError):
    """Raised when login credentials are invalid."""


class RepositoryError(GasManagementError):
    """Raised when a database/storage operation fails."""


class CustomerNotFoundError(RepositoryError):
    """Raised when a requested customer does not exist."""


class DuplicateCustomerError(RepositoryError):
    """Raised when creating a customer whose account number already exists."""
