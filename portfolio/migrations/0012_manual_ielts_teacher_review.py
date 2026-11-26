from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio", "0011_ielts_assignment_ai_assessment"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="ieltsassignmentsubmission",
            name="ai_band_score",
        ),
        migrations.RemoveField(
            model_name="ieltsassignmentsubmission",
            name="ai_feedback",
        ),
        migrations.RemoveField(
            model_name="ieltsassignmentsubmission",
            name="ai_status",
        ),
        migrations.RemoveField(
            model_name="ieltsassignmentsubmission",
            name="extracted_text",
        ),
        migrations.RemoveField(
            model_name="ieltsassignmentsubmission",
            name="word_count",
        ),
        migrations.AddField(
            model_name="ieltsassignmentsubmission",
            name="teacher_strengths",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="ieltsassignmentsubmission",
            name="teacher_improvements",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="ieltsassignmentsubmission",
            name="corrected_sentences",
            field=models.TextField(blank=True, help_text="Teacher-written sentence corrections and explanations"),
        ),
    ]
