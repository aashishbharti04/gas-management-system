"""Run the web dashboard:  python -m gas_management.web

Also exposed as the ``gas-management-web`` console script.
"""

from __future__ import annotations

from .app import create_app


def main() -> None:
    try:
        import uvicorn
    except ImportError as exc:  # pragma: no cover - depends on optional extra
        raise SystemExit(
            "The web dashboard needs extra packages. Install them with:\n"
            "    pip install gas-management-system[web]"
        ) from exc

    from ..config import Settings

    settings = Settings.from_env()
    uvicorn.run(create_app(settings), host=settings.web_host, port=settings.web_port)


if __name__ == "__main__":
    main()
