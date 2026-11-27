from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("attendance", "0004_studentprofile_user"),
        ("portfolio", "0021_ieltsassignment_corrected_answer"),
    ]

    operations = [
        migrations.AddField(
            model_name="ieltsassignment",
            name="target_student",
            field=models.ForeignKey(
                blank=True,
                help_text="When set, this assignment is visible only to the selected student. Leave empty for course-wide assignments.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="individual_ielts_assignments",
                to="attendance.studentprofile",
            ),
        ),
    ]
