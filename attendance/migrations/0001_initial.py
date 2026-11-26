import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="StudentProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(db_index=True, max_length=120)),
                ("roll", models.CharField(blank=True, max_length=40)),
                ("course", models.CharField(choices=[("IELTS", "IELTS"), ("Language Testing", "Language Testing"), ("Programming", "Programming"), ("CSE Course", "CSE Course"), ("School Academy", "School Academy"), ("College Academy", "College Academy"), ("Undergraduate Courses", "Undergraduate Courses"), ("BCS", "BCS")], max_length=40)),
                ("modules", models.JSONField(default=list, help_text="Modules assigned to this student")),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ("course", "name")},
        ),
        migrations.CreateModel(
            name="AttendanceRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("class_date", models.DateField(db_index=True)),
                ("period", models.CharField(choices=[("AM", "AM"), ("PM", "PM")], max_length=2)),
                ("course_name", models.CharField(max_length=40)),
                ("module_name", models.CharField(max_length=120)),
                ("sign_in", models.TimeField(blank=True, null=True)),
                ("sign_out", models.TimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="attendance_records", to="attendance.studentprofile")),
            ],
            options={"ordering": ("-class_date", "period", "student__name")},
        ),
        migrations.AddConstraint(model_name="studentprofile", constraint=models.UniqueConstraint(fields=("name", "roll", "course"), name="unique_student_course_roll")),
        migrations.AddConstraint(model_name="attendancerecord", constraint=models.UniqueConstraint(fields=("class_date", "student", "period"), name="unique_attendance_student_period_day")),
    ]
