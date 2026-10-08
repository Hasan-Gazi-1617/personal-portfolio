from django.contrib import admin

from .models import ComplaintTicket, TicketActivity


@admin.register(ComplaintTicket)
class ComplaintTicketAdmin(admin.ModelAdmin):
    list_display = ("tki_id", "client_id", "field_support_engineer", "higher_level_noc", "status", "dependency", "attention", "opened_at")
    list_filter = ("status", "dependency", "field_support_engineer", "higher_level_noc", "attention", "isp_related")
    search_fields = ("tki_id", "client_id", "complaint", "remarks", "findings")
    autocomplete_fields = ("assigned_engineer", "created_by")
    readonly_fields = ("created_at", "updated_at", "support_assigned_at", "resolved_at")


@admin.register(TicketActivity)
class TicketActivityAdmin(admin.ModelAdmin):
    list_display = ("ticket", "actor", "action", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("ticket__tki_id", "actor__username", "detail")
    readonly_fields = ("ticket", "actor", "action", "detail", "created_at")
