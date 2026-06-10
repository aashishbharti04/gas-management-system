"""Shared brand metadata used by both the CLI and the web dashboard.

Keeping these in one place means the footer/contact details are defined once and
stay consistent across every front-end.
"""

from __future__ import annotations

APP_NAME = "Gas Management System"
TAGLINE = "Secure CNG / LPG billing & inventory"

CONTACT_EMAIL = "aashish@marketdoctorsonline.com"

# Ordered so the UI renders them consistently.
SOCIAL_LINKS: dict[str, str] = {
    "LinkedIn": "https://in.linkedin.com/in/aashana1012",
    "GitHub": "https://github.com/aashishbharti04",
    "YouTube": "https://www.youtube.com/@CodeWithAsur",
    "Instagram": "https://www.instagram.com/asurwave1012",
}

OPEN_SOURCE_NOTICE = (
    "This project is open source and available for educational, "
    "learning, and community contributions."
)
COPYRIGHT = f"© {APP_NAME}. All rights reserved."
