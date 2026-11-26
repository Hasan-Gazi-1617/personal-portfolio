from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('attendance', '0004_studentprofile_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentprofile',
            name='joining_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='studentprofile',
            name='course_finish_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
