from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('attendance', '0004_studentprofile_user'),
        ('portfolio', '0016_ielts_assignment_attempt_locking'),
    ]

    operations = [
        migrations.AddField(
            model_name='ieltsassignmentsubmission',
            name='student_profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ielts_submissions', to='attendance.studentprofile'),
        ),
    ]
