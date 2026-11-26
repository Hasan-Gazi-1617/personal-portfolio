# Remove the optional AI-only fields; assignment marking is teacher-led.
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio", "0011_ielts_assignment_ai_assessment"),
    ]

    operations = [
        migrations.RemoveField(model_name="ieltsassignmentsubmission", name="ai_band_score"),
        migrations.RemoveField(model_name="ieltsassignmentsubmission", name="ai_feedback"),
        migrations.RemoveField(model_name="ieltsassignmentsubmission", name="ai_status"),
        migrations.RemoveField(model_name="ieltsassignmentsubmission", name="extracted_text"),
        migrations.RemoveField(model_name="ieltsassignmentsubmission", name="word_count"),
    ]
