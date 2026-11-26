# Initial database migration for the IELTS student learning area.
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("portfolio", "0008_olt_monitoring")]

    operations = [
        migrations.CreateModel(name="IELTSNotice", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("title", models.CharField(max_length=180)), ("message", models.TextField()),
            ("is_published", models.BooleanField(db_index=True, default=True)),
            ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)),
        ], options={"ordering": ("-created_at",)}),
        migrations.CreateModel(name="IELTSMaterial", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("title", models.CharField(max_length=180)), ("description", models.TextField(blank=True)),
            ("category", models.CharField(choices=[("general","General"),("grammar","Grammar"),("speaking","Speaking"),("writing","Writing"),("reading","Reading"),("listening","Listening")], default="general", max_length=16)),
            ("resource_url", models.URLField(blank=True)), ("file", models.FileField(blank=True, upload_to="ielts/materials/")),
            ("is_published", models.BooleanField(db_index=True, default=True)), ("created_at", models.DateTimeField(auto_now_add=True)),
        ], options={"ordering": ("category", "-created_at")}),
        migrations.CreateModel(name="IELTSLesson", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("title", models.CharField(max_length=180)),
            ("skill", models.CharField(choices=[("general","General"),("grammar","Grammar"),("speaking","Speaking"),("writing","Writing"),("reading","Reading"),("listening","Listening")], default="general", max_length=16)),
            ("summary", models.CharField(blank=True, max_length=280)), ("content", models.TextField()),
            ("order", models.PositiveIntegerField(default=0)), ("is_published", models.BooleanField(db_index=True, default=True)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
        ], options={"ordering": ("order", "title")}),
        migrations.CreateModel(name="IELTSPracticeSet", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("title", models.CharField(max_length=180)), ("skill", models.CharField(choices=[("reading","Reading"),("writing","Writing"),("speaking","Speaking"),("listening","Listening")], db_index=True, max_length=12)),
            ("instructions", models.TextField(blank=True)), ("time_minutes", models.PositiveSmallIntegerField(default=20)),
            ("questions", models.JSONField(blank=True, default=list)), ("is_published", models.BooleanField(db_index=True, default=False)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
        ], options={"ordering": ("skill", "-created_at")}),
        migrations.CreateModel(name="IELTSPracticeAttempt", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("student_name", models.CharField(max_length=100)), ("student_roll", models.CharField(blank=True, max_length=40)),
            ("answers", models.JSONField(default=dict)), ("objective_score", models.PositiveSmallIntegerField(blank=True, null=True)),
            ("total_objective", models.PositiveSmallIntegerField(blank=True, null=True)),
            ("ai_score", models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True)),
            ("ai_feedback", models.TextField(blank=True)), ("submitted_at", models.DateTimeField(auto_now_add=True)),
            ("practice", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attempts", to="portfolio.ieltspracticeset")),
        ], options={"ordering": ("-submitted_at",)}),
        migrations.CreateModel(name="IELTSAttendance", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("class_date", models.DateField(db_index=True)), ("batch", models.CharField(default="IELTS", max_length=100)),
            ("topic", models.CharField(blank=True, max_length=180)), ("roster", models.JSONField(blank=True, default=list)),
            ("updated_at", models.DateTimeField(auto_now=True)),
        ], options={"ordering": ("-class_date", "batch"), "constraints": [models.UniqueConstraint(fields=("class_date", "batch"), name="unique_ielts_attendance_batch_date")]}),
        migrations.CreateModel(name="IELTSAssignment", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("title", models.CharField(max_length=180)), ("instructions", models.TextField()),
            ("deadline", models.DateTimeField(blank=True, null=True)), ("is_published", models.BooleanField(db_index=True, default=True)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
        ], options={"ordering": ("-created_at",)}),
        migrations.CreateModel(name="IELTSAssignmentSubmission", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("student_name", models.CharField(max_length=100)), ("student_roll", models.CharField(blank=True, max_length=40)),
            ("answer_text", models.TextField(blank=True)), ("file", models.FileField(blank=True, upload_to="ielts/assignments/")),
            ("teacher_feedback", models.TextField(blank=True)), ("marked_fragments", models.JSONField(blank=True, default=list)),
            ("score", models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True)),
            ("reviewed_at", models.DateTimeField(blank=True, null=True)), ("submitted_at", models.DateTimeField(auto_now_add=True)),
            ("assignment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="submissions", to="portfolio.ieltsassignment")),
        ], options={"ordering": ("-submitted_at",)}),
    ]
