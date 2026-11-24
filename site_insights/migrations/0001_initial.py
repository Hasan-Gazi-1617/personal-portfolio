# Generated for visitor analytics and newsletter subscriptions
import uuid
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='DailyVisitor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visitor_key', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('visit_date', models.DateField(db_index=True, default=django.utils.timezone.localdate)),
                ('first_path', models.CharField(blank=True, max_length=300)),
                ('source', models.CharField(blank=True, max_length=120)),
                ('device', models.CharField(choices=[('mobile','Mobile'),('desktop','Desktop'),('tablet','Tablet'),('other','Other')], default='other', max_length=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering':['-visit_date','-created_at']},
        ),
        migrations.CreateModel(
            name='NewsletterSubscriber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('subscribed_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('unsubscribe_token', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('consent_text', models.CharField(default='I agree to receive portfolio updates by email.', max_length=180)),
            ],
            options={'ordering':['-subscribed_at']},
        ),
        migrations.CreateModel(
            name='PageView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('viewed_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('visit_date', models.DateField(db_index=True, default=django.utils.timezone.localdate)),
                ('path', models.CharField(db_index=True, max_length=300)),
                ('source', models.CharField(blank=True, max_length=120)),
                ('device', models.CharField(default='other', max_length=12)),
            ],
            options={'ordering':['-viewed_at']},
        ),
        migrations.CreateModel(
            name='SiteEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.CharField(choices=[('cv_download','CV download'),('project_click','Project click')], db_index=True, max_length=24)),
                ('path', models.CharField(blank=True, max_length=300)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={'ordering':['-created_at']},
        ),
        migrations.AddConstraint(
            model_name='dailyvisitor',
            constraint=models.UniqueConstraint(fields=('visitor_key','visit_date'), name='uniq_visitor_per_day'),
        ),
    ]
