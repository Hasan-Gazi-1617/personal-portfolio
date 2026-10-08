from datetime import datetime

from django.db import migrations
from django.utils import timezone


def seed_tki_register(apps, schema_editor):
    ComplaintTicket = apps.get_model("portfolio", "ComplaintTicket")
    from portfolio.management.commands.import_tki_seed import RECORDS

    field_engineers = {"abir", "faruk", "prodosh", "rukunuzzaman"}
    noc_engineers = {"farzana", "hasan", "jewel", "riaz"}
    high_priority = {3, 4, 5, 15, 23, 25, 34, 36, 37, 38, 39, 40}
    technician_issues = {"Cable Cut", "Down for Resource Work"}

    for serial, cpid, raw_date, customer, issue, support, contact, detail in RECORDS:
        opened = timezone.make_aware(datetime.strptime(raw_date, "%d-%b-%Y").replace(hour=12))
        support_key = support.lower()
        ComplaintTicket.objects.update_or_create(
            tki_id=f"TKI-{opened:%Y%m%d}-{serial:03d}",
            defaults={
                "client_id": cpid,
                "opened_at": opened,
                "status": "pending",
                "dependency": "technician" if issue in technician_issues else "support_engineer",
                "field_support_engineer": support_key if support_key in field_engineers else "",
                "higher_level_noc": support_key if support_key in noc_engineers else "",
                "priority": "high" if serial in high_priority else "medium",
                "category": "fiber" if issue in technician_issues | {"No Connection"} else "router",
                "complaint": f"{issue} — {customer}",
                "remarks": " | ".join(part for part in (contact and f"Contact: {contact}", detail) if part),
                "attention": issue in technician_issues,
            },
        )


class Migration(migrations.Migration):
    dependencies = [("portfolio", "0002_complaintticket_attention_complaintticket_dependency_and_more")]
    operations = [migrations.RunPython(seed_tki_register, migrations.RunPython.noop)]
