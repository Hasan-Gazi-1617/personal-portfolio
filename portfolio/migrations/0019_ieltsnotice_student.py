from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("attendance", "0006_studentcourse_enrollment"),
        ("portfolio", "0018_course_scoped_learning_content"),
    ]

    operations = [
        migrations.AddField(
            model_name="ieltsnotice",
            name="student",
            field=models.ForeignKey(
                blank=True,
                help_text="Leave empty to publish to all students in the selected course",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="personal_notices",
                to="attendance.studentprofile",
            ),
        ),
    ]
