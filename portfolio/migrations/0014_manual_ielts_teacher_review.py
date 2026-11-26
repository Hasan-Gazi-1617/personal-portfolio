from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio", "0013_teacher_ielts_criterion_bands"),
    ]

    operations = [
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
