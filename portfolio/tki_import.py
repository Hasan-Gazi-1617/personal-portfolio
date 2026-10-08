import hashlib
import unicodedata
from datetime import datetime, timedelta

from django.utils import timezone


def import_solved_tsv(text, Ticket):
    field_engineers = {"abir", "faruk", "prodosh", "rukunuzzaman"}
    noc_engineers = {"farzana", "hasan", "jewel", "riaz"}
    billing_terms = ("bill", "billing", "package")
    fiber_terms = ("cable cut", "resource work", "dbm high", "line shifting", "room shifting")
    created = updated = skipped = 0

    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lower().startswith("sl."):
            continue
        # NFC keeps Bangla vowel signs and conjuncts in one consistent Unicode
        # representation, regardless of which editor exported the UTF-8 file.
        fields = [unicodedata.normalize("NFC", value.strip()) for value in line.split("\t")]
        if len(fields) != 14 or not fields[0].rstrip(".").isdigit():
            skipped += 1
            continue
        serial = int(fields[0].rstrip("."))
        raw_date, cpid, customer, issue = fields[1:5]
        received_by, support_by, visited_by = (value.strip().lower() for value in fields[5:8])
        saved_number, unsaved_number, details, feedback, status = fields[8:13]
        if status.lower() != "solved":
            skipped += 1
            continue
        try:
            opened = timezone.make_aware(datetime.strptime(raw_date, "%d %b %Y").replace(hour=12))
        except ValueError:
            skipped += 1
            continue

        normalize = lambda value: {"faruq": "faruk", "juwel": "jewel"}.get(value, value)
        received_by, support_by, visited_by = map(normalize, (received_by, support_by, visited_by))
        fingerprint = "|".join((raw_date, cpid, customer, issue, saved_number, unsaved_number, details, feedback))
        import_key = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:12]
        marker = f"Private import: {import_key}"
        notes = [marker]
        if saved_number:
            notes.append(f"Saved: {saved_number}")
        if unsaved_number:
            notes.append(f"Other: {unsaved_number}")
        if details:
            notes.append(details)
        if feedback:
            notes.append(feedback)
        issue_clean = " ".join(issue.split())
        issue_lower = issue_clean.lower()
        field_engineer = next((name for name in (visited_by, support_by, received_by) if name in field_engineers), "")
        noc_engineer = next((name for name in (support_by, received_by) if name in noc_engineers), "")
        dependency = "technician" if any(term in issue_lower for term in fiber_terms) else ("manor_other_team" if any(term in issue_lower for term in billing_terms) else "support_engineer")
        category = "fiber" if any(term in issue_lower for term in fiber_terms + ("no connection",)) else ("billing" if any(term in issue_lower for term in billing_terms) else "router")
        defaults = {
            "client_id": cpid,
            "opened_at": opened,
            "status": "solved",
            "dependency": dependency,
            "field_support_engineer": field_engineer,
            "higher_level_noc": noc_engineer,
            "priority": "medium",
            "category": category,
            "complaint": f"{issue_clean} — {customer}",
            "remarks": " | ".join(notes),
            "attention": False,
            "resolved_at": opened + timedelta(hours=1),
            "resolution": feedback or details or "Solved",
        }
        existing = Ticket.objects.filter(remarks__contains=marker).first()
        if existing is None:
            existing = Ticket.objects.filter(client_id=cpid, opened_at__date=opened.date(), complaint__istartswith=issue_clean, status="pending").order_by("id").first()
        if existing:
            for key, value in defaults.items():
                setattr(existing, key, value)
            existing.save()
            updated += 1
        else:
            _, was_created = Ticket.objects.update_or_create(
                tki_id=f"SOLVED-{opened:%Y%m%d}-{import_key.upper()}", defaults=defaults
            )
            created += int(was_created)
            updated += int(not was_created)
    return {"created": created, "updated": updated, "skipped": skipped}
