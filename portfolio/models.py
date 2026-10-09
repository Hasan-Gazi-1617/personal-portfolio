from datetime import timedelta

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


class ComplaintTicket(models.Model):
    class Category(models.TextChoices):
        FIBER = "fiber", "Fiber Cut"
        WIFI = "wifi", "WIFI Problem"
        ROUTER_CONFIG = "router_config", "Router Configuration"
        BILLING = "billing", "Billing Issue"
        ONU = "onu", "ONU Faulty"
        LINK_DOWN = "link_down", "Link Down"
        ROUTER = "router", "Router Problem"
        PASSWORD = "password", "Password Change"
        SHIFTING = "shifting", "Shifting"
        INSTALLATION = "installation", "Installation"
        GAMING = "gaming", "Gaming Problem"
        WEBSITE = "website", "Website Problem"
        BANDWIDTH = "bandwidth", "Bandwidth Problem"
        BROWSING = "browsing", "Browsing Problem"
        PON_DOWN = "pon_down", "PON Down"
        OLT = "olt", "OLT Problem / Malfunction"
        CORE_ROUTER = "core_router", "Core Router Problem / Malfunction"
        IIG = "iig", "IIG Issue"
        PPPOE = "pppoe", "PPPoE / Authentication"
        SLOW = "slow", "Slow Internet"
        ISP = "isp", "ISP / Upstream"
        OTHER = "other", "Other"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SOLVED = "solved", "TKI Solved"
        CANCELLED = "cancelled", "Cancelled"

    class Dependency(models.TextChoices):
        TECHNICIAN = "technician", "Technician"
        ISP = "isp", "ISP"
        SUPPORT = "support_engineer", "Support Engineer"
        NOC = "noc_engineer", "NOC Engineer"
        CUSTOMER = "customer", "Customer"
        OTHER_TEAM = "manor_other_team", "Other Team"

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

    class RepeatReason(models.TextChoices):
        CUSTOMER = "customer", "Customer-related"
        ENGINEER = "engineer", "Engineer-related"
        DEPENDENCY = "dependency", "External dependency"
        OTHER = "other", "Other / Under review"

    class ReceivedBy(models.TextChoices):
        ABIR = "abir", "Abir"
        FARUK = "faruk", "Faruk"
        PRODOSH = "prodosh", "Prodosh"
        RUKUNUZZAMAN = "rukunuzzaman", "Rukunuzzaman"
        HASAN = "hasan", "Hasan"
        JEWEL = "jewel", "Jewel"
        RIAZ = "riaz", "Riaz"
        FARZANA = "farzana", "Farzana"

    tki_id = models.CharField(max_length=40, unique=True, validators=[
        RegexValidator(r"^[A-Za-z0-9._/-]+$", "Use letters, numbers, dot, slash, underscore or hyphen only.")
    ])
    client_id = models.CharField(max_length=40, db_index=True)
    opened_at = models.DateTimeField()
    category = models.CharField(max_length=24, choices=Category.choices, default=Category.OTHER)
    priority = models.CharField(max_length=12, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.PENDING, db_index=True)
    dependency = models.CharField(max_length=24, choices=Dependency.choices, blank=True, db_index=True)
    higher_level_noc = models.CharField(max_length=20, choices=NocEngineer.choices, blank=True, db_index=True)
    received_by = models.CharField(max_length=24, choices=ReceivedBy.choices, blank=True, db_index=True)
    support_by = models.CharField(max_length=24, choices=ReceivedBy.choices, blank=True, db_index=True)
    visited_by = models.CharField(max_length=24, choices=ReceivedBy.choices, blank=True, db_index=True)
    field_support_engineer = models.CharField(max_length=24, choices=SupportEngineer.choices, blank=True, db_index=True)
    field_support_done = models.BooleanField(default=False, db_index=True)
    noc_field_visit_done = models.BooleanField(default=False, db_index=True)
    remarks = models.TextField(blank=True)
    attention = models.BooleanField(default=False, db_index=True)
    isp_related = models.BooleanField(default=False)
    complaint = models.TextField()
    assigned_engineer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_tickets")
    support_assigned_at = models.DateTimeField(null=True, blank=True)
    findings = models.TextField(blank=True)
    troubleshooting = models.TextField(blank=True)
    resolution = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    sla_hours = models.PositiveSmallIntegerField(default=0, help_text="SLA target in hours; can be overridden per ticket.")
    dependency_started_at = models.DateTimeField(null=True, blank=True)
    dependency_paused_seconds = models.PositiveBigIntegerField(default=0)
    repeat_reason = models.CharField(max_length=20, choices=RepeatReason.choices, blank=True)
    repeat_note = models.TextField(blank=True)
    repeat_engineer = models.CharField(max_length=24, choices=ReceivedBy.choices, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="created_tickets")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-opened_at", "-id")
        indexes = [models.Index(fields=("client_id", "opened_at"), name="tki_client_opened_idx")]

    def __str__(self):
        return f"{self.tki_id} · {self.client_id}"

    @property
    def engineer_support(self):
        return bool(self.field_support_engineer or self.assigned_engineer_id)

    @staticmethod
    def default_sla_hours(category):
        if category == "fiber":
            return 4
        if category in {"password", "billing"}:
            return 1
        if category in {"wifi", "gaming", "website", "browsing", "bandwidth", "slow"}:
            return 2
        if category in {"router", "router_config", "onu", "link_down", "pon_down"}:
            return 3
        if category in {"installation", "shifting"}:
            return 24
        return 4

    def elapsed_sla_seconds(self, at=None):
        at = at or timezone.now()
        end = self.resolved_at or at
        total = max(0, int((end - self.opened_at).total_seconds()))
        paused = self.dependency_paused_seconds
        if self.dependency and self.dependency_started_at:
            paused += max(0, int((end - self.dependency_started_at).total_seconds()))
        return max(0, total - paused)

    @property
    def sla_breached(self):
        return self.elapsed_sla_seconds() > self.sla_hours * 3600

    @property
    def sla_elapsed_display(self):
        minutes = self.elapsed_sla_seconds() // 60
        return f"{minutes // 60}h {minutes % 60}m"

    @property
    def aging(self):
        end = self.resolved_at or timezone.now()
        delta = max(end - self.opened_at, timedelta())
        days, remainder = divmod(int(delta.total_seconds()), 86400)
        hours, _ = divmod(remainder, 3600)
        return f"{days}d {hours}h" if days else f"{hours}h"

    def save(self, *args, **kwargs):
        now = timezone.now()
        if not self.sla_hours:
            self.sla_hours = self.default_sla_hours(self.category)
        if self.pk:
            old = type(self).objects.filter(pk=self.pk).only("dependency", "dependency_started_at", "dependency_paused_seconds", "status", "resolved_at").first()
            if old:
                was_paused = bool(old.dependency and old.dependency_started_at)
                is_paused = bool(self.dependency)
                if is_paused and not was_paused:
                    self.dependency_started_at = now
                elif was_paused and not is_paused:
                    self.dependency_paused_seconds = old.dependency_paused_seconds + max(
                        0, int((now - old.dependency_started_at).total_seconds())
                    )
                    self.dependency_started_at = None
                elif is_paused:
                    self.dependency_started_at = old.dependency_started_at or now
        elif self.dependency:
            self.dependency_started_at = now
        if self.status == self.Status.SOLVED and not self.resolved_at:
            self.resolved_at = now
        elif self.status != self.Status.SOLVED:
            self.resolved_at = None
        super().save(*args, **kwargs)


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
