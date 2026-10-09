from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("portfolio", "0004_complaintticket_field_support_done_and_more")]

    operations = [
        migrations.AlterField(
            model_name="complaintticket",
            name="status",
            field=models.CharField(
                choices=[("pending", "Pending"), ("solved", "TKI Solved"), ("cancelled", "Cancelled")],
                db_index=True, default="pending", max_length=24,
            ),
        ),
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
        migrations.AddField(
            model_name="complaintticket", name="received_by",
            field=models.CharField(blank=True, choices=[
                ("abir", "Abir"), ("faruk", "Faruk"), ("prodosh", "Prodosh"),
                ("rukunuzzaman", "Rukunuzzaman"), ("hasan", "Hasan"), ("jewel", "Jewel"),
                ("riaz", "Riaz"), ("farzana", "Farzana"),
            ], db_index=True, max_length=24),
        ),
        migrations.AddField(
            model_name="complaintticket", name="support_by",
            field=models.CharField(blank=True, choices=[
                ("abir", "Abir"), ("faruk", "Faruk"), ("prodosh", "Prodosh"),
                ("rukunuzzaman", "Rukunuzzaman"), ("hasan", "Hasan"), ("jewel", "Jewel"),
                ("riaz", "Riaz"), ("farzana", "Farzana"),
            ], db_index=True, max_length=24),
        ),
        migrations.AddField(
            model_name="complaintticket", name="visited_by",
            field=models.CharField(blank=True, choices=[
                ("abir", "Abir"), ("faruk", "Faruk"), ("prodosh", "Prodosh"),
                ("rukunuzzaman", "Rukunuzzaman"), ("hasan", "Hasan"), ("jewel", "Jewel"),
                ("riaz", "Riaz"), ("farzana", "Farzana"),
            ], db_index=True, max_length=24),
        ),
        migrations.AddField(
            model_name="complaintticket", name="sla_hours",
            field=models.PositiveSmallIntegerField(default=4, help_text="SLA target in hours; can be overridden per ticket."),
        ),
        migrations.AddField(
            model_name="complaintticket", name="dependency_started_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="complaintticket", name="dependency_paused_seconds",
            field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="complaintticket", name="repeat_reason",
            field=models.CharField(blank=True, choices=[
                ("customer", "Customer-related"), ("engineer", "Engineer-related"),
                ("dependency", "External dependency"), ("other", "Other / Under review"),
            ], max_length=20),
        ),
        migrations.AddField(
            model_name="complaintticket", name="repeat_note",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="complaintticket", name="repeat_engineer",
            field=models.CharField(blank=True, choices=[
                ("abir", "Abir"), ("faruk", "Faruk"), ("prodosh", "Prodosh"),
                ("rukunuzzaman", "Rukunuzzaman"), ("hasan", "Hasan"), ("jewel", "Jewel"),
                ("riaz", "Riaz"), ("farzana", "Farzana"),
            ], max_length=24),
        ),
        migrations.AddIndex(
            model_name="complaintticket",
            index=models.Index(fields=["client_id", "opened_at"], name="tki_client_opened_idx"),
        ),
    ]
