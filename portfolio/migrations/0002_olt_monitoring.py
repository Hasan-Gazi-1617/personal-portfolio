# Generated for the private OLT monitoring dashboard.
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("portfolio", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="OLTDevice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("identifier", models.SlugField(max_length=80, unique=True)),
                ("name", models.CharField(max_length=120)),
                ("vendor", models.CharField(max_length=40, default="other")),
                ("location", models.CharField(max_length=160, blank=True)),
                ("management_ip", models.GenericIPAddressField(blank=True, null=True)),
                ("pon_port_count", models.PositiveSmallIntegerField(default=0)),
                ("is_enabled", models.BooleanField(default=True)),
                ("last_seen", models.DateTimeField(blank=True, null=True, db_index=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="ONUStatus",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("onu_id", models.CharField(max_length=100)),
                ("pon_port", models.CharField(max_length=40, blank=True)),
                ("status", models.CharField(max_length=12, choices=[("online", "Online"), ("offline", "Offline"), ("unknown", "Unknown")], default="unknown", db_index=True)),
                ("serial_number", models.CharField(max_length=100, blank=True)),
                ("last_seen", models.DateTimeField(blank=True, null=True)),
                ("status_changed_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("olt", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="onus", to="portfolio.oltdevice")),
            ],
            options={"ordering": ("olt__name", "pon_port", "onu_id"), "constraints": [models.UniqueConstraint(fields=("olt", "onu_id"), name="unique_onu_per_olt")]},
        ),
        migrations.CreateModel(
            name="OLTEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("onu_id", models.CharField(max_length=100)),
                ("pon_port", models.CharField(max_length=40, blank=True)),
                ("event_type", models.CharField(max_length=12, choices=[("online", "Online"), ("offline", "Offline")])),
                ("occurred_at", models.DateTimeField(db_index=True)),
                ("details", models.CharField(max_length=240, blank=True)),
                ("olt", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="events", to="portfolio.oltdevice")),
            ],
            options={"ordering": ("-occurred_at",)},
        ),
    ]
