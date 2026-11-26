from django.db import migrations, models
import django.db.models.deletion


def link_existing_student_records(apps, schema_editor):
    StudentProfile = apps.get_model("attendance", "StudentProfile")
    PracticeAttempt = apps.get_model("portfolio", "IELTSPracticeAttempt")
    AssignmentSubmission = apps.get_model("portfolio", "IELTSAssignmentSubmission")
    for attempt in PracticeAttempt.objects.filter(student_profile__isnull=True).iterator():
        matches = StudentProfile.objects.filter(name__iexact=attempt.student_name, roll=attempt.student_roll)
        if matches.count() == 1:
            attempt.student_profile_id = matches.first().pk
            attempt.save(update_fields=["student_profile"])
    for submission in AssignmentSubmission.objects.filter(student_profile__isnull=True).iterator():
        matches = StudentProfile.objects.filter(name__iexact=submission.student_name, roll=submission.student_roll)
        if matches.count() == 1:
            submission.student_profile_id = matches.first().pk
            submission.save(update_fields=["student_profile"])


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
        migrations.RunPython(link_existing_student_records, migrations.RunPython.noop),
    ]
