from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="OLTDevice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.SlugField(max_length=64, unique=True)),
                ("name", models.CharField(max_length=120)),
                ("management_url", models.URLField(blank=True)),
                ("active", models.BooleanField(default=True)),
                ("last_seen", models.DateTimeField(blank=True, null=True)),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="ONUStatus",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("pon_id", models.CharField(max_length=32)),
                ("onu_id", models.CharField(max_length=32)),
                ("serial", models.CharField(blank=True, max_length=64)),
                ("description", models.CharField(blank=True, max_length=255)),
                ("status", models.CharField(choices=[("online", "Online"), ("offline", "Offline")], default="offline", max_length=12)),
                ("down_reason", models.CharField(blank=True, max_length=120)),
                ("last_change", models.DateTimeField()),
                ("last_seen", models.DateTimeField()),
                ("last_up", models.DateTimeField(blank=True, null=True)),
                ("last_down", models.DateTimeField(blank=True, null=True)),
                ("olt", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="onus", to="portfolio.oltdevice")),
            ],
            options={
                "ordering": ("olt__name", "pon_id", "onu_id"),
                "indexes": [
                    models.Index(fields=["olt", "pon_id", "status"], name="onu_olt_pon_status_idx"),
                    models.Index(fields=["status", "last_change"], name="onu_status_change_idx"),
                ],
                "constraints": [
                    models.UniqueConstraint(fields=("olt", "pon_id", "onu_id"), name="unique_olt_pon_onu")
                ],
            },
        ),
        migrations.CreateModel(
            name="ONUEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("event_type", models.CharField(choices=[("up", "Up"), ("down", "Down")], max_length=8)),
                ("occurred_at", models.DateTimeField()),
                ("previous_status", models.CharField(blank=True, max_length=12)),
                ("status", models.CharField(max_length=12)),
                ("reason", models.CharField(blank=True, max_length=120)),
                ("onu", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="events", to="portfolio.onustatus")),
            ],
            options={
                "ordering": ("-occurred_at",),
                "indexes": [models.Index(fields=["event_type", "occurred_at"], name="onu_event_time_idx")],
            },
        ),
    ]
