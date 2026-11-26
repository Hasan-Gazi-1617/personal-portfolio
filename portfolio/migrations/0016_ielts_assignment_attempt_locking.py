from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio", "0015_ielts_assignment_timing_word_limits"),
    ]

    operations = [
        migrations.AddField(
            model_name="ieltsassignmentsubmission",
            name="status",
            field=models.CharField(choices=[("in_progress", "In Progress"), ("submitted", "Submitted"), ("failed", "Failed")], db_index=True, default="submitted", max_length=16),
        ),
        migrations.AddField(
            model_name="ieltsassignmentsubmission",
            name="paste_attempts",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="ieltsassignmentsubmission",
            name="started_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="ieltsassignmentsubmission",
            name="failed_reason",
            field=models.TextField(blank=True),
        ),
    ]
