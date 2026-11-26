from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio", "0014_manual_ielts_teacher_review"),
    ]

    operations = [
        migrations.AddField(
            model_name="ieltsassignment",
            name="time_minutes",
            field=models.PositiveSmallIntegerField(default=40, help_text="IELTS writing task duration in minutes"),
        ),
        migrations.AddField(
            model_name="ieltsassignment",
            name="min_words",
            field=models.PositiveSmallIntegerField(default=250, help_text="Minimum required word count"),
        ),
        migrations.AddField(
            model_name="ieltsassignment",
            name="max_words",
            field=models.PositiveSmallIntegerField(default=350, help_text="Maximum permitted word count"),
        ),
        migrations.AddField(
            model_name="ieltsassignmentsubmission",
            name="word_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="ieltsassignmentsubmission",
            name="elapsed_seconds",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
