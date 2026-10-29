import json
import logging
import os
import re

logger = logging.getLogger(__name__)

# Keep the public contact link usable even when the Render environment
# variable has not been configured. Render's PUBLIC_CONTACT_EMAIL overrides it.
DEFAULT_PUBLIC_EMAIL = "mh.jewel.1617@gmail.com"

# Searchable locations grouped by OLT and PON port. OLT URLs are matched
# against PRIVATE_NAV_LINKS_JSON so the search opens the existing configured login page.
OLT_LOCATION_MAP = [
    ("OLT 10", "VSOL", [
        ("Rikabibazar", 1), ("Kazitula", 2), ("Mirzajangal", 4),
    ]),
    ("OLT 11", "VSOL-OLD", [
        ("Muttalib Villa", 1), ("Kazi Elias", 2), ("Kalighat Old", 3), ("Kalighat New", 4),
    ]),
    ("OLT 12", "C-DATA", [
        ("Housing Estate", 1), ("Pirmoholla", 1), ("Amberkhana", 1), ("Boroikandi", 2), ("Technical Road", 2), ("Lawai", 2), ("Rikabibazar", 3),
        ("Munshipara", 3), ("Kuarpar", 3), ("Lamabazar", 3), ("Shukria Market", 5), ("Puranlane", 5), ("Zindabazar", 5),
    ]),
    ("OLT 14", "C-DATA", [
        ("Galleria, Raja Mansion", 1), ("Blue Water, Kakoli Shopping Center", 1), ("Kaniz Plaza, West World", 1), ("Milennium, Asia Market", 2), ("Mitali Mansion, London Mansion", 2),
        ("Noyashorok, Hawapara", 3), ("Nehar Market, Mirboxtula", 3), ("Taltola", 4), ("Sheikhghat", 5),
        ("Lamabazr, Bhatalia", 6), ("Vhartokhola-Chondipul", 7), ("Kumarpara", 8),
    ]),
    ("OLT 15", "C-DATA", [
        ("Amberkhana", 1), ("Jalalabad", 2), ("Mojumdari- Badambagicha", 3),
        ("Baluchor", 4), ("Soudaghortula-Mirabazar", 5), ("Uposhohor-D Block", 6),
        ("Chowkidekhi", 7), ("Borobazar- S. Eidgah", 8),
    ]),
    ("OLT 16", "C-DATA", [
        ("Modinamarket-Pathantula", 1), ("Bagbari", 2), ("Sagordighirpar", 3),
        ("Kalibari", 4), ("Neharipara", 5), ("Borobari", 6),
        ("Shamimabad", 7), ("Nobabroad", 8),
    ]),
    ("OLT 17", "C-DATA", [
        ("Mejortila", 1), ("Khadimpara", 2), ("Surmagate, Doloipara", 3),
    ]),
    ("OLT 18", "C-DATA", [
        ("Akhalia, Surma Abashik", 1), ("Mahmudabad- Chorugaw, Shahebergaw", 2),
        ("Thanabari", 3), ("Shining City", 3), ("Taker Bari", 3), ("Shiber Bazar", 3), ("Badaghat", 3), ("Haydorpur", 4),("Khaligaw", 4),
        ("N. Khurumkhola", 5), ("Uttorpirpur", 5), ("Pirpur", 6),
        ("Tukerbazar", 7), ("Shahpur", 7), ("Tukergaw", 8), ("Nuagaw", 8),
    ]),
    ("OLT 19", "C-DATA", [
        ("Subidbazar", 1), ("Kodomtoli new", 2), ("Dariapara, Jallarpar", 3),
        ("Shibgonj", 4), ("Baruthkhana", 5), ("Dorgah, Mirermoydan", 6),
        ("Uposhohor Block-F-J", 7), ("Naiorpool to Mendibag", 8),
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
        # Environment labels identify OLTs by their numeric menu ID (for example,
        # "OLT VSOL EPON:10"), not necessarily by the text "OLT 10".
        olt_number_match = re.search(r"\d+", olt_name)
        olt_number = olt_number_match.group(0) if olt_number_match else ""
        url = next(
            (
                str(endpoint.get("url", ""))
                for endpoint in menu
                if isinstance(endpoint, dict)
                and endpoint.get("url")
                and (
                    olt_name.casefold() in str(endpoint.get("label", "")).casefold()
                    or (
                        olt_number
                        and re.search(
                            rf":\s*{re.escape(olt_number)}\s*$",
                            str(endpoint.get("label", "")).strip(),
                        )
                    )
                )
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
    if not request.session.get("owner_access") and not request.session.get("olt_user_access"):
        return {
            "private_links": {},
            "olt_locations": [],
            "public_email": public_email,
            "networking_lessons_url": os.environ.get("NETWORKING_LESSONS_URL", "#"),
        }

    configured_links = _json_env("PRIVATE_NAV_LINKS_JSON", {})
    if request.session.get("owner_access"):
        private_links = configured_links
    else:
        # OLT-only users must not receive other private navigation links.
        private_links = {"olt_menu": configured_links.get("olt_menu", [])} if isinstance(configured_links, dict) else {}
    # Use only the maintained OLT_LOCATION_MAP. Do not append OLT_LOCATIONS_JSON:
    # stale environment entries can reintroduce old/duplicate PON locations in search.
    olt_locations = _build_olt_locations(private_links)

    return {
        "private_links": private_links,
        "olt_locations": olt_locations,
        "public_email": public_email,
        "networking_lessons_url": os.environ.get("NETWORKING_LESSONS_URL", "#"),
    }
