from django.contrib import admin
from .models import DailyVisitor, PageView, SiteEvent, ModuleUsage


@admin.register(DailyVisitor)
class DailyVisitorAdmin(admin.ModelAdmin):
    list_display = ('visit_date', 'visitor_key', 'first_path', 'source', 'device')
    list_filter = ('visit_date', 'device', 'source')
    search_fields = ('first_path', 'source')
    readonly_fields = ('visitor_key', 'visit_date', 'first_path', 'source', 'device', 'created_at')


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('viewed_at', 'path', 'source', 'device')
    list_filter = ('visit_date', 'device', 'source')
    search_fields = ('path', 'source')
    readonly_fields = ('viewed_at', 'visit_date', 'path', 'source', 'device')


@admin.register(SiteEvent)
class SiteEventAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'event', 'path')
    list_filter = ('event', 'created_at')
    readonly_fields = ('created_at', 'event', 'path')


@admin.register(ModuleUsage)
class ModuleUsageAdmin(admin.ModelAdmin):
    list_display = ('visit_date', 'module', 'visitor_key', 'created_at')
    list_filter = ('visit_date', 'module')
    search_fields = ('module',)
    readonly_fields = ('visit_date', 'module', 'visitor_key', 'created_at')
