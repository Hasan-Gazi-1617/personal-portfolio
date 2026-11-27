from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("attendance", "0007_studentprofile_access_code")]

    operations = [
        migrations.AddField(model_name="studentprofile", name="email", field=models.EmailField(blank=True, max_length=254)),
        migrations.AddField(model_name="studentprofile", name="address", field=models.TextField(blank=True)),
        migrations.AddField(model_name="studentprofile", name="country", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="studentprofile", name="city", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="studentprofile", name="cell_phone", field=models.CharField(blank=True, max_length=30)),
        migrations.AddField(model_name="studentprofile", name="date_of_birth", field=models.DateField(blank=True, null=True)),
    ]
