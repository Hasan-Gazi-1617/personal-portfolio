# Generated for IELTS assignment AI assessment fields.
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio", "0010_ielts_submission_receipt"),
    ]

    operations = [
        migrations.AddField(
            model_name="ieltsassignmentsubmission",
            name="ai_band_score",
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=3, null=True),
        ),
        migrations.AddField(
            model_name="ieltsassignmentsubmission",
            name="ai_feedback",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="ieltsassignmentsubmission",
            name="ai_status",
            field=models.CharField(default="pending", max_length=24),
        ),
        migrations.AddField(
            model_name="ieltsassignmentsubmission",
            name="extracted_text",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="ieltsassignmentsubmission",
            name="word_count",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
