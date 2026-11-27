from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("portfolio", "0019_ieltsnotice_student"),
    ]

    operations = [
        migrations.AddField(
            model_name="ieltsassignment",
            name="module_name",
            field=models.CharField(blank=True, default="", max_length=120),
        ),
    ]
