from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("attendance", "0006_studentcourse_enrollment"),
        ("portfolio", "0017_ielts_submission_student_profile"),
    ]

    operations = [
        migrations.AddField(model_name="ieltsnotice", name="course", field=models.CharField(db_index=True, default="IELTS", help_text="Only students enrolled in this course can access this content", max_length=40)),
        migrations.AddField(model_name="ieltsmaterial", name="course", field=models.CharField(db_index=True, default="IELTS", help_text="Only students enrolled in this course can access this content", max_length=40)),
        migrations.AddField(model_name="ieltslesson", name="course", field=models.CharField(db_index=True, default="IELTS", help_text="Only students enrolled in this course can access this content", max_length=40)),
        migrations.AddField(model_name="ieltspracticeset", name="course", field=models.CharField(db_index=True, default="IELTS", help_text="Only students enrolled in this course can access this content", max_length=40)),
        migrations.AddField(model_name="ieltsassignment", name="course", field=models.CharField(db_index=True, default="IELTS", help_text="Only students enrolled in this course can access this content", max_length=40)),
        migrations.AddField(model_name="ieltspracticeattempt", name="student_profile", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="practice_attempts", to="attendance.studentprofile")),
    ]
