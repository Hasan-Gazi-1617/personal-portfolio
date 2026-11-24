import uuid
from django.db import models
from django.utils import timezone


class DailyVisitor(models.Model):
    visitor_key = models.UUIDField(default=uuid.uuid4, editable=False)
    visit_date = models.DateField(default=timezone.localdate, db_index=True)
    first_path = models.CharField(max_length=300, blank=True)
    source = models.CharField(max_length=120, blank=True)
    device = models.CharField(max_length=12, choices=[('mobile','Mobile'),('desktop','Desktop'),('tablet','Tablet'),('other','Other')], default='other')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=('visitor_key','visit_date'), name='uniq_visitor_per_day')]
        ordering = ['-visit_date','-created_at']

    def __str__(self):
        return f'{self.visit_date} · {self.visitor_key}'


class PageView(models.Model):
    viewed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    visit_date = models.DateField(default=timezone.localdate, db_index=True)
    path = models.CharField(max_length=300, db_index=True)
    source = models.CharField(max_length=120, blank=True)
    device = models.CharField(max_length=12, default='other')

    class Meta:
        ordering = ['-viewed_at']

    def __str__(self):
        return f'{self.visit_date} {self.path}'


class SiteEvent(models.Model):
    EVENT_CHOICES = [('cv_download','CV download'),('project_click','Project click')]
    event = models.CharField(max_length=24, choices=EVENT_CHOICES, db_index=True)
    path = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']


class ModuleUsage(models.Model):
    visitor_key = models.UUIDField(editable=False)
    visit_date = models.DateField(default=timezone.localdate, db_index=True)
    module = models.SlugField(max_length=80, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=('visitor_key', 'visit_date', 'module'), name='uniq_module_visitor_day')]
        ordering = ['-visit_date', 'module']

    def __str__(self):
        return f'{self.visit_date} · {self.module}'
