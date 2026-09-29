import json
import logging
import os

logger = logging.getLogger(__name__)


def _json_env(name, fallback):
    raw = os.environ.get(name, "")
    if not raw:
        return fallback
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        logger.error("Invalid JSON in %s; private navigation data was not loaded", name)
        return fallback
    return value


def private_navigation(request):
    """Expose private infrastructure links only inside an unlocked owner session."""
    if not request.session.get("owner_access"):
        return {
            "private_links": {},
            "olt_locations": [],
            "public_email": os.environ.get("PUBLIC_CONTACT_EMAIL", ""),
            "networking_lessons_url": os.environ.get("NETWORKING_LESSONS_URL", "#"),
        }
    return {
        "private_links": _json_env("PRIVATE_NAV_LINKS_JSON", {}),
        "olt_locations": _json_env("OLT_LOCATIONS_JSON", []),
        "public_email": os.environ.get("PUBLIC_CONTACT_EMAIL", ""),
        "networking_lessons_url": os.environ.get("NETWORKING_LESSONS_URL", "#"),
    }
