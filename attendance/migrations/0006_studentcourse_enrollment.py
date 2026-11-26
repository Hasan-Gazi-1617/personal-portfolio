from django.db import migrations, models
import django.db.models.deletion


def copy_existing_enrollments(apps, schema_editor):
    StudentProfile = apps.get_model("attendance", "StudentProfile")
    StudentCourse = apps.get_model("attendance", "StudentCourse")
    for student in StudentProfile.objects.all().iterator():
        StudentCourse.objects.get_or_create(
            student_id=student.pk,
            course=student.course,
            defaults={
                "modules": student.modules or [],
                "joining_date": student.joining_date,
                "course_finish_date": student.course_finish_date,
                "is_active": student.is_active,
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("attendance", "0005_studentprofile_course_dates"),
    ]

    operations = [
        migrations.CreateModel(
            name="StudentCourse",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("course", models.CharField(choices=[("IELTS", "IELTS"), ("Language Testing", "Language Testing"), ("Programming", "Programming"), ("CSE Course", "CSE Course"), ("School Academy", "School Academy"), ("College Academy", "College Academy"), ("Undergraduate Courses", "Undergraduate Courses"), ("BCS", "BCS")], max_length=40)),
                ("modules", models.JSONField(default=list, help_text="Modules assigned for this course")),
                ("joining_date", models.DateField(blank=True, null=True)),
                ("course_finish_date", models.DateField(blank=True, null=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="course_enrollments", to="attendance.studentprofile")),
            ],
            options={"ordering": ("course",)},
        ),
        migrations.AddConstraint(
            model_name="studentcourse",
            constraint=models.UniqueConstraint(fields=("student", "course"), name="unique_student_course_enrollment"),
        ),
        migrations.RunPython(copy_existing_enrollments, migrations.RunPython.noop),
    ]
