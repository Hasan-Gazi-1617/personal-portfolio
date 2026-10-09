from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("portfolio", "0005_tki_sla_repeat_fields")]

    operations = [
        migrations.AddField(
            model_name="complaintticket",
            name="support_type",
            field=models.CharField(
                choices=[("phone", "Phone Support"), ("field", "Field Support"), ("noc", "NOC Support")],
                db_index=True, default="phone", max_length=12,
            ),
        ),
    ]
