from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("attendance", "0001_initial"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="attendancerecord",
            name="unique_attendance_student_period_day",
        ),
    ]
