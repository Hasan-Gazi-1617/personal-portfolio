from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [('site_insights', '0001_initial')]
    operations = [
        migrations.DeleteModel(name='NewsletterSubscriber'),
        migrations.CreateModel(
            name='ModuleUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visitor_key', models.UUIDField(editable=False)),
                ('visit_date', models.DateField(db_index=True, default=django.utils.timezone.localdate)),
                ('module', models.SlugField(db_index=True, max_length=80)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['-visit_date', 'module']},
        ),
        migrations.AddConstraint(
            model_name='moduleusage',
            constraint=models.UniqueConstraint(fields=('visitor_key', 'visit_date', 'module'), name='uniq_module_visitor_day'),
        ),
    ]
