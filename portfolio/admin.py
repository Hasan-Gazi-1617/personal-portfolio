from django.contrib import admin

from .models import OLTDevice, ONUEvent, ONUStatus


@admin.register(OLTDevice)
class OLTDeviceAdmin(admin.ModelAdmin):
    list_display = ("name", "key", "active", "last_seen")
    search_fields = ("name", "key")


@admin.register(ONUStatus)
class ONUStatusAdmin(admin.ModelAdmin):
    list_display = ("client_label", "olt", "pon_id", "onu_id", "status", "last_change")
    list_filter = ("olt", "pon_id", "status")
    search_fields = ("description", "serial", "pon_id", "onu_id")


@admin.register(ONUEvent)
class ONUEventAdmin(admin.ModelAdmin):
    list_display = ("onu", "event_type", "occurred_at", "reason")
    list_filter = ("event_type", "onu__olt")
    search_fields = ("onu__description", "onu__serial", "reason")
