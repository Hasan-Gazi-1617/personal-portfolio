from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("portfolio", "0020_ieltsassignment_module_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="ieltsassignmentsubmission",
            name="corrected_answer",
            field=models.TextField(blank=True, help_text="Teacher's corrected version for side-by-side word comparison"),
        ),
    ]
