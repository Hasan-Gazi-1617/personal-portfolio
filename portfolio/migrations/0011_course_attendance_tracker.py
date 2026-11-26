from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("portfolio", "0010_ielts_submission_receipt")]

    operations = [
        migrations.CreateModel(
            name="IELTSStudent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, unique=True)),
                ("roll", models.CharField(blank=True, db_index=True, max_length=40)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="CourseAttendance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("class_date", models.DateField(db_index=True)),
                ("course_name", models.CharField(choices=[("IELTS", "IELTS"), ("Language Testing", "Language Testing"), ("Programming", "Programming"), ("CSE Course", "CSE Course"), ("School Academy", "School Academy"), ("College Academy", "College Academy"), ("Undergraduate Courses", "Undergraduate Courses"), ("BCS", "BCS")], db_index=True, max_length=40)),
                ("module_name", models.CharField(max_length=100)),
                ("sign_in", models.TimeField()),
                ("sign_out", models.TimeField()),
                ("duration_minutes", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attendance_records", to="portfolio.ieltsstudent")),
            ],
            options={"ordering": ("-class_date", "-sign_in", "student__name")},
        ),
        migrations.AddIndex(model_name="courseattendance", index=models.Index(fields=["student", "class_date"], name="course_att_student_date_idx")),
    ]
