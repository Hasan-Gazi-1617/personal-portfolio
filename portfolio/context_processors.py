import json
import logging
import os

logger = logging.getLogger(__name__)

# Keep the public contact link usable even when the Render environment
# variable has not been configured. Render's PUBLIC_CONTACT_EMAIL overrides it.
DEFAULT_PUBLIC_EMAIL = "mh.jewel.1617@gmail.com"

# Searchable locations grouped by OLT and PON port. OLT URLs are matched
# against PRIVATE_NAV_LINKS_JSON so the search opens the existing configured login page.
OLT_LOCATION_MAP = [
    ("OLT 10", "Vsol", [
        ("Rikabibazar", 1), ("Kazitula", 2), ("Shukria Market", 3), ("Mirjajungle", 4),
    ]),
    ("OLT 11", "Vsol-Old", [
        ("Muttalib Villa", 1), ("Kazielias", 2), ("Kalighat old", 3), ("Kalighat New", 4),
    ]),
    ("OLT 12", "C-dada Backup", [
        ("Housingestate", 1), ("Boroikandi", 2), ("Rikabibazar-Munshi para", 3),
    ]),
    ("OLT 14", "", [
        ("Galleria, Rajamension", 1), ("Millennium, Asia Market, Mitalimension", 2),
        ("Noyashorok", 3), ("Taltola", 4), ("Sheikhghat", 5),
        ("Lamabazr, Bhatalia", 6), ("Vhartokhola-chondipul", 7), ("Kumarpara", 8),
    ]),
    ("OLT 15", "", [
        ("Amberkhana", 1), ("Jalalabad", 2), ("Mojumdari- Badambagicha", 3),
        ("Baluchor", 4), ("Soudaghortula-Mirabazar", 5), ("Uposhohor-D Block", 6),
        ("Chowkidekhi", 7), ("Borobazar- S. Eidgah", 8),
    ]),
    ("OLT 16", "", [
        ("Modinamarket- Pathantula", 1), ("Bagbari", 2), ("Sagordighirpar", 3),
        ("Kalibari", 4), ("Neharipara", 5), ("Borobari", 6),
        ("Shamimabad", 7), ("Nobabroad", 8),
    ]),
    ("OLT 17", "", [
        ("Mejortila", 1), ("Khadimpara", 2), ("Surmagate, Doloipara", 3),
    ]),
    ("OLT 18", "", [
        ("Akhalia, Surma Abashik", 1), ("Mahmudabad- Chorugaw, Shahebergaw", 2),
        ("Thanabari, Shinning City", 3), ("Haydorpur, Khaligaw", 4),
        ("N. Khurumkhola, Uttorpirpur", 5), ("Pirpur", 6),
        ("Tukerbazar, Shahpur", 7), ("Tukergaw, Nuagaw", 8),
    ]),
    ("OLT 19", "", [
        ("Subidbazar", 1), ("Kodomtoli new", 2), ("Dariapara, Jallarpar", 3),
        ("Shibgonj", 4), ("Baruthkhana", 5), ("Dorgah, Mirermoydan", 6),
        ("Uposhohor Block-F-J", 7), ("Niorpool to Mendibug", 8),
    ]),
]


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


def _build_olt_locations(private_links):
    """Build search entries using configured OLT menu URLs, without exposing credentials."""
    menu = private_links.get("olt_menu", []) if isinstance(private_links, dict) else []
    locations = []
    for olt_name, vendor, pon_entries in OLT_LOCATION_MAP:
        url = next(
            (
                str(endpoint.get("url", ""))
                for endpoint in menu
                if isinstance(endpoint, dict)
                and olt_name.casefold() in str(endpoint.get("label", "")).casefold()
                and endpoint.get("url")
            ),
            "",
        )
        for location, port in pon_entries:
            locations.append({
                "location": location,
                "olt": olt_name,
                "pop": vendor,
                "port": f"PON-{port}",
                "url": url,
            })
    return locations


def private_navigation(request):
    """Expose private infrastructure links only inside an unlocked owner session."""
    public_email = os.environ.get("PUBLIC_CONTACT_EMAIL", "").strip() or DEFAULT_PUBLIC_EMAIL
    if not request.session.get("owner_access"):
        return {
            "private_links": {},
            "olt_locations": [],
            "public_email": public_email,
            "networking_lessons_url": os.environ.get("NETWORKING_LESSONS_URL", "#"),
        }

    private_links = _json_env("PRIVATE_NAV_LINKS_JSON", {})
    configured_locations = _json_env("OLT_LOCATIONS_JSON", [])
    if not isinstance(configured_locations, list):
        configured_locations = []
    # Always include the built-in PON map; environment-configured entries are
    # appended so an empty/stale OLT_LOCATIONS_JSON cannot hide the new locations.
    mapped_locations = _build_olt_locations(private_links)
    known_keys = {
        (str(item.get("location", "")).strip().casefold(),
         str(item.get("olt", "")).strip().casefold(),
         str(item.get("port", "")).strip().casefold())
        for item in mapped_locations
    }
    extra_locations = [
        item for item in configured_locations
        if isinstance(item, dict) and
        (str(item.get("location", "")).strip().casefold(),
         str(item.get("olt", "")).strip().casefold(),
         str(item.get("port", "")).strip().casefold()) not in known_keys
    ]
    olt_locations = mapped_locations + extra_locations

    return {
        "private_links": private_links,
        "olt_locations": olt_locations,
        "public_email": public_email,
        "networking_lessons_url": os.environ.get("NETWORKING_LESSONS_URL", "#"),
    }
