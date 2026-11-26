from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("attendance", "0002_allow_multiple_attendance_sessions"),
    ]

    operations = [
        migrations.AddField(
            model_name="attendancerecord",
            name="sign_out_date",
            field=models.DateField(
                blank=True,
                help_text="Bangladesh-local date when the student signed out",
                null=True,
            ),
        ),
    ]
