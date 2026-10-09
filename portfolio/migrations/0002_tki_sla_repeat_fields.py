from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("portfolio", "0001_initial")]

    operations = [
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
