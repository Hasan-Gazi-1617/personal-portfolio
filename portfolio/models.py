from django.db import models


class OLTDevice(models.Model):
    key = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=120)
    management_url = models.URLField(blank=True)
    active = models.BooleanField(default=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class ONUStatus(models.Model):
    ONLINE = "online"
    OFFLINE = "offline"
    STATUS_CHOICES = ((ONLINE, "Online"), (OFFLINE, "Offline"))

    olt = models.ForeignKey(OLTDevice, on_delete=models.CASCADE, related_name="onus")
    pon_id = models.CharField(max_length=32)
    onu_id = models.CharField(max_length=32)
    serial = models.CharField(max_length=64, blank=True)
    description = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=OFFLINE)
    down_reason = models.CharField(max_length=120, blank=True)
    last_change = models.DateTimeField()
    last_seen = models.DateTimeField()
    last_up = models.DateTimeField(null=True, blank=True)
    last_down = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("olt__name", "pon_id", "onu_id")
        constraints = [
            models.UniqueConstraint(fields=("olt", "pon_id", "onu_id"), name="unique_olt_pon_onu")
        ]
        indexes = [
            models.Index(fields=("olt", "pon_id", "status"), name="onu_olt_pon_status_idx"),
            models.Index(fields=("status", "last_change"), name="onu_status_change_idx"),
        ]

    @property
    def client_label(self):
        return self.description or self.serial or f"ONU {self.onu_id}"

    def __str__(self):
        return f"{self.olt.key} {self.pon_id}/{self.onu_id} {self.client_label}"


class ONUEvent(models.Model):
    UP = "up"
    DOWN = "down"
    EVENT_CHOICES = ((UP, "Up"), (DOWN, "Down"))

    onu = models.ForeignKey(ONUStatus, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=8, choices=EVENT_CHOICES)
    occurred_at = models.DateTimeField()
    previous_status = models.CharField(max_length=12, blank=True)
    status = models.CharField(max_length=12)
    reason = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ("-occurred_at",)
        indexes = [
            models.Index(fields=("event_type", "occurred_at"), name="onu_event_time_idx"),
        ]

    def __str__(self):
        return f"{self.onu.client_label} {self.event_type} at {self.occurred_at}"
