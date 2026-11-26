from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('attendance', '0003_attendancerecord_sign_out_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentprofile',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='student_profile', to=settings.AUTH_USER_MODEL),
        ),
    ]
