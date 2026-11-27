from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("bcs_exam", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.AddField(model_name="bcsexam", name="model_test_number", field=models.PositiveIntegerField(default=1)),
        migrations.AddField(model_name="bcsattempt", name="teacher_score", field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
        migrations.AddField(model_name="bcsattempt", name="teacher_feedback", field=models.TextField(blank=True)),
        migrations.AddField(model_name="bcsattempt", name="reviewed_at", field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name="bcsattempt", name="reviewed_by", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="reviewed_bcs_attempts", to=settings.AUTH_USER_MODEL)),
    ]
