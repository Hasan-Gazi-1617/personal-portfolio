from django.db import migrations, models


def normalize_legacy_statuses(apps, schema_editor):
    Ticket = apps.get_model("portfolio", "ComplaintTicket")
    Ticket.objects.filter(status__in=["open", "assigned", "in_progress", "feedback_pending"]).update(status="pending")
    Ticket.objects.filter(status__in=["resolved", "closed"]).update(status="solved")


class Migration(migrations.Migration):
    dependencies = [("portfolio", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="complaintticket", name="status",
            field=models.CharField(choices=[("pending","Pending"),("solved","TKI Solved"),("cancelled","Cancelled")], db_index=True, default="pending", max_length=24),
        ),
        migrations.RunPython(normalize_legacy_statuses, migrations.RunPython.noop),
        migrations.AddField(
            model_name="complaintticket", name="dependency",
            field=models.CharField(blank=True, choices=[("technician","Technician"),("isp","ISP"),("support_engineer","Support Engineer"),("noc_engineer","NOC Engineer"),("customer","Customer"),("manor_other_team","Other Team")], db_index=True, max_length=24),
        ),
        migrations.AddField(
            model_name="complaintticket", name="higher_level_noc",
            field=models.CharField(blank=True, choices=[("farzana","Farzana"),("hasan","Hasan"),("jewel","Jewel"),("riaz","Riaz")], db_index=True, max_length=20),
        ),
        migrations.AddField(
            model_name="complaintticket", name="field_support_engineer",
            field=models.CharField(blank=True, choices=[("abir","Abir"),("faruk","Faruk"),("prodosh","Prodosh"),("rukunuzzaman","Rukunuzzaman")], db_index=True, max_length=24),
        ),
        migrations.AddField("complaintticket", "field_support_done", models.BooleanField(db_index=True, default=False, help_text="Selected field engineer completed support")),
        migrations.AddField("complaintticket", "noc_field_visit_done", models.BooleanField(db_index=True, default=False, help_text="Selected NOC engineer completed a field visit")),
        migrations.AddField("complaintticket", "remarks", models.TextField(blank=True, help_text="Latest/last operational comment")),
        migrations.AddField("complaintticket", "attention", models.BooleanField(db_index=True, default=False)),

        migrations.AlterField(
            model_name="complaintticket",
            name="category",
            field=models.CharField(
                choices=[
                    ("fiber", "Fiber Cut"), ("wifi", "WIFI Problem"),
                    ("router_config", "Router Configuration"), ("billing", "Billing Issue"),
                    ("onu", "ONU Faulty"), ("link_down", "Link Down"),
                    ("router", "Router Problem"), ("password", "Password Change"),
                    ("shifting", "Shifting"), ("installation", "Installation"),
                    ("gaming", "Gaming Problem"), ("website", "Website Problem"),
                    ("bandwidth", "Bandwidth Problem"), ("browsing", "Browsing Problem"),
                    ("pon_down", "PON Down"), ("olt", "OLT Problem / Malfunction"),
                    ("core_router", "Core Router Problem / Malfunction"), ("iig", "IIG Issue"),
                    ("pppoe", "PPPoE / Authentication"), ("slow", "Slow Internet"),
                    ("isp", "ISP / Upstream"), ("other", "Other"),
                ],
                default="other", max_length=24,
            ),
        ),
        migrations.AddField("complaintticket", "received_by", models.CharField(blank=True, choices=[("abir","Abir"),("faruk","Faruk"),("prodosh","Prodosh"),("rukunuzzaman","Rukunuzzaman"),("hasan","Hasan"),("jewel","Jewel"),("riaz","Riaz"),("farzana","Farzana")], db_index=True, max_length=24)),
        migrations.AddField("complaintticket", "support_by", models.CharField(blank=True, choices=[("abir","Abir"),("faruk","Faruk"),("prodosh","Prodosh"),("rukunuzzaman","Rukunuzzaman"),("hasan","Hasan"),("jewel","Jewel"),("riaz","Riaz"),("farzana","Farzana")], db_index=True, max_length=24)),
        migrations.AddField("complaintticket", "visited_by", models.CharField(blank=True, choices=[("abir","Abir"),("faruk","Faruk"),("prodosh","Prodosh"),("rukunuzzaman","Rukunuzzaman"),("hasan","Hasan"),("jewel","Jewel"),("riaz","Riaz"),("farzana","Farzana")], db_index=True, max_length=24)),
        migrations.AddField("complaintticket", "sla_hours", models.PositiveSmallIntegerField(default=4, help_text="SLA target in hours; can be overridden per ticket.")),
        migrations.AddField("complaintticket", "dependency_started_at", models.DateTimeField(blank=True, null=True)),
        migrations.AddField("complaintticket", "dependency_paused_seconds", models.PositiveBigIntegerField(default=0)),
        migrations.AddField("complaintticket", "repeat_reason", models.CharField(blank=True, choices=[("customer","Customer-related"),("engineer","Engineer-related"),("dependency","External dependency"),("other","Other / Under review")], max_length=20)),
        migrations.AddField("complaintticket", "repeat_note", models.TextField(blank=True)),
        migrations.AddField("complaintticket", "repeat_engineer", models.CharField(blank=True, choices=[("abir","Abir"),("faruk","Faruk"),("prodosh","Prodosh"),("rukunuzzaman","Rukunuzzaman"),("hasan","Hasan"),("jewel","Jewel"),("riaz","Riaz"),("farzana","Farzana")], max_length=24)),
        migrations.AddIndex("complaintticket", models.Index(fields=["client_id", "opened_at"], name="tki_client_opened_idx")),
    ]
