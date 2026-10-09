from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("portfolio", "0006_tki_support_type")]

    operations = [
        migrations.AddField(
            model_name="complaintticket",
            name="status_type",
            field=models.CharField(
                choices=[("new", "New"), ("follow_up", "Follow-up"), ("repeat", "Repeat")],
                db_index=True, default="new", max_length=12,
            ),
        ),
    ]
