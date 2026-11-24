import csv
from django.contrib import admin
from django.http import HttpResponse
from .models import DailyVisitor, PageView, SiteEvent, NewsletterSubscriber


@admin.action(description='Export selected active subscriber emails as CSV')
def export_subscribers(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="newsletter-subscribers.csv"'
    writer = csv.writer(response)
    writer.writerow(['Email','Subscribed at','Active'])
    for row in queryset.filter(is_active=True):
        writer.writerow([row.email,row.subscribed_at.isoformat(),row.is_active])
    return response


@admin.register(DailyVisitor)
class DailyVisitorAdmin(admin.ModelAdmin):
    list_display = ('visit_date','visitor_key','first_path','source','device')
    list_filter = ('visit_date','device','source')
    search_fields = ('first_path','source')
    readonly_fields = ('visitor_key','visit_date','first_path','source','device','created_at')


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('viewed_at','path','source','device')
    list_filter = ('visit_date','device','source')
    search_fields = ('path','source')
    readonly_fields = ('viewed_at','visit_date','path','source','device')


@admin.register(SiteEvent)
class SiteEventAdmin(admin.ModelAdmin):
    list_display = ('created_at','event','path')
    list_filter = ('event','created_at')
    readonly_fields = ('created_at','event','path')


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email','subscribed_at','is_active')
    list_filter = ('is_active','subscribed_at')
    search_fields = ('email',)
    readonly_fields = ('subscribed_at','unsubscribe_token')
    actions = (export_subscribers,)
