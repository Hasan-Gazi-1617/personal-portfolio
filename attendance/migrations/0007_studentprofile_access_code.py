import secrets
import attendance.models
from django.db import migrations, models


def populate_student_access_codes(apps, schema_editor):
    StudentProfile = apps.get_model("attendance", "StudentProfile")
    database = schema_editor.connection.alias
    for student in StudentProfile.objects.using(database).filter(access_code__isnull=True).iterator():
        while True:
            code = secrets.token_hex(5).upper()
            if not StudentProfile.objects.using(database).filter(access_code=code).exists():
                student.access_code = code
                student.save(update_fields=["access_code"], using=database)
                break


class Migration(migrations.Migration):
    dependencies = [
        ("attendance", "0006_studentcourse_enrollment"),
    ]

    operations = [
        migrations.AddField(
            model_name="studentprofile",
            name="access_code",
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.RunPython(populate_student_access_codes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="studentprofile",
            name="access_code",
            field=models.CharField(default=attendance.models.generate_student_access_code, editable=False, max_length=10, unique=True),
        ),
    ]
