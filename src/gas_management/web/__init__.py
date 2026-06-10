"""Optional FastAPI web dashboard for the Gas Management System.

The dashboard reuses the same configuration, storage layer, authentication, and
business services as the CLI — it is purely an additional front-end.

Install the extra dependencies with::

    pip install gas-management-system[web]

Then run::

    python -m gas_management.web        # or: gas-management-web
"""

from __future__ import annotations

from .app import create_app

__all__ = ["create_app"]
