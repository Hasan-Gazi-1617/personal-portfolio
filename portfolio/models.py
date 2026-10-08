from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


class ComplaintTicket(models.Model):
    class Category(models.TextChoices):
        FIBER = "fiber", "Fiber / LOS"
        ROUTER = "router", "Router / Wi-Fi"
        PPPOE = "pppoe", "PPPoE / Authentication"
        SLOW = "slow", "Slow Internet"
        BILLING = "billing", "Billing"
        OLT = "olt", "OLT / ONU"
        ISP = "isp", "ISP / Upstream"
        OTHER = "other", "Other"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SOLVED = "solved", "Solved"
        CANCELLED = "cancelled", "Cancelled"

    class Dependency(models.TextChoices):
        TECHNICIAN = "technician", "Technician"
        ISP = "isp", "ISP"
        SUPPORT = "support_engineer", "Support Engineer"
        NOC = "noc_engineer", "NOC Engineer"
        CUSTOMER = "customer", "Customer"
        OTHER_TEAM = "manor_other_team", "Manor Other Team"

    class SupportEngineer(models.TextChoices):
        ABIR = "abir", "Abir"
        FARUK = "faruk", "Faruk"
        PRODOSH = "prodosh", "Prodosh"
        RUKUNUZZAMAN = "rukunuzzaman", "Rukunuzzaman"

    class NocEngineer(models.TextChoices):
        FARZANA = "farzana", "Farzana"
        HASAN = "hasan", "Hasan"
        JEWEL = "jewel", "Jewel"
        RIAZ = "riaz", "Riaz"

    tki_id = models.CharField(
        max_length=40,
        unique=True,
        validators=[RegexValidator(r"^[A-Za-z0-9._/-]+$", "Use letters, numbers, dot, slash, underscore or hyphen only.")],
    )
    client_id = models.CharField(max_length=40, db_index=True)
    opened_at = models.DateTimeField()
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    priority = models.CharField(max_length=12, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.PENDING, db_index=True)
    dependency = models.CharField(max_length=24, choices=Dependency.choices, blank=True, db_index=True)
    higher_level_noc = models.CharField(max_length=20, choices=NocEngineer.choices, blank=True, db_index=True)
    field_support_engineer = models.CharField(max_length=24, choices=SupportEngineer.choices, blank=True, db_index=True)
    field_support_done = models.BooleanField(default=False, db_index=True, help_text="Selected field engineer completed support")
    noc_field_visit_done = models.BooleanField(default=False, db_index=True, help_text="Selected NOC engineer completed a field visit")
    remarks = models.TextField(blank=True, help_text="Latest/last operational comment")
    attention = models.BooleanField(default=False, db_index=True)
    isp_related = models.BooleanField(default=False)
    complaint = models.TextField()
    assigned_engineer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_tickets",
    )
    support_assigned_at = models.DateTimeField(null=True, blank=True)
    findings = models.TextField(blank=True)
    troubleshooting = models.TextField(blank=True)
    resolution = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="created_tickets",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-opened_at", "-id")

    def __str__(self):
        return f"{self.tki_id} · {self.client_id}"

    @property
    def engineer_support(self):
        return bool(self.field_support_engineer or self.assigned_engineer_id)

    @property
    def aging(self):
        from django.utils import timezone

        end = self.resolved_at or timezone.now()
        delta = max(end - self.opened_at, timezone.timedelta())
        days, remainder = divmod(int(delta.total_seconds()), 86400)
        hours, _ = divmod(remainder, 3600)
        return f"{days}d {hours}h" if days else f"{hours}h"


class TicketActivity(models.Model):
    ticket = models.ForeignKey(ComplaintTicket, on_delete=models.CASCADE, related_name="activities")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=120)
    detail = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.ticket.tki_id}: {self.action}"
