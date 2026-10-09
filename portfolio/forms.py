from django import forms
from django.contrib.auth import get_user_model

from .models import ComplaintTicket

User = get_user_model()


class DateTimeLocalInput(forms.DateTimeInput):
    input_type = "datetime-local"


class AdminTicketForm(forms.ModelForm):
    class Meta:
        model = ComplaintTicket
        fields = (
            "tki_id", "client_id", "opened_at", "category", "priority", "sla_hours",
            "received_by", "support_by", "support_type", "visited_by", "higher_level_noc",
            "status", "dependency", "resolved_at", "field_support_engineer",
            "field_support_done", "noc_field_visit_done", "repeat_reason",
            "repeat_note", "repeat_engineer", "attention", "remarks", "isp_related",
            "complaint", "assigned_engineer", "findings", "troubleshooting", "resolution",
        )
        widgets = {
            "opened_at": DateTimeLocalInput(format="%Y-%m-%dT%H:%M"),
            "resolved_at": DateTimeLocalInput(format="%Y-%m-%dT%H:%M"),
            "complaint": forms.Textarea(attrs={"rows": 3}),
            "findings": forms.Textarea(attrs={"rows": 2}),
            "troubleshooting": forms.Textarea(attrs={"rows": 2}),
            "resolution": forms.Textarea(attrs={"rows": 2}),
            "remarks": forms.Textarea(attrs={"rows": 2, "placeholder": "Latest update / last comment"}),
            "repeat_note": forms.Textarea(attrs={"rows": 2, "placeholder": "Repeat issue notes"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["opened_at"].input_formats = ("%Y-%m-%dT%H:%M",)
        self.fields["resolved_at"].input_formats = ("%Y-%m-%dT%H:%M",)
        self.fields["status"].choices = (
            (ComplaintTicket.Status.PENDING, ComplaintTicket.Status.PENDING.label),
            (ComplaintTicket.Status.SOLVED, ComplaintTicket.Status.SOLVED.label),
        )
        self.fields["assigned_engineer"].queryset = User.objects.filter(
            is_active=True, is_staff=False
        ).order_by("first_name", "username")
        self.fields["assigned_engineer"].required = False
        self.fields["sla_hours"].min_value = 1
        self.fields["sla_hours"].help_text = "Default is selected from issue type; admin can adjust."
        if not self.instance.pk and not self.initial.get("sla_hours"):
            self.initial["sla_hours"] = ComplaintTicket.default_sla_hours(
                self.initial.get("category", ComplaintTicket.Category.OTHER)
            )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("field_support_done") and not cleaned.get("field_support_engineer"):
            self.add_error("field_support_engineer", "Select the field engineer who completed support.")
        if cleaned.get("noc_field_visit_done") and not cleaned.get("higher_level_noc"):
            self.add_error("higher_level_noc", "Select the NOC engineer who completed the field visit.")
        if cleaned.get("repeat_reason") == ComplaintTicket.RepeatReason.ENGINEER and not cleaned.get("repeat_engineer"):
            self.add_error("repeat_engineer", "Select the engineer responsible for this repeat.")
        return cleaned


class EngineerTicketUpdateForm(forms.ModelForm):
    class Meta:
        model = ComplaintTicket
        fields = (
            "status", "dependency", "higher_level_noc", "noc_field_visit_done",
            "field_support_engineer", "field_support_done", "support_by", "visited_by",
            "attention", "remarks", "findings", "troubleshooting", "resolution",
        )
        widgets = {
            "findings": forms.Textarea(attrs={"rows": 3}),
            "troubleshooting": forms.Textarea(attrs={"rows": 4}),
            "resolution": forms.Textarea(attrs={"rows": 3}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("field_support_done") and not cleaned.get("field_support_engineer"):
            self.add_error("field_support_engineer", "Select the field engineer who completed support.")
        if cleaned.get("noc_field_visit_done") and not cleaned.get("higher_level_noc"):
            self.add_error("higher_level_noc", "Select the NOC engineer who completed the field visit.")
        if cleaned.get("status") == ComplaintTicket.Status.SOLVED:
            if not cleaned.get("findings") or not cleaned.get("troubleshooting"):
                raise forms.ValidationError("Findings and troubleshooting are required before resolving or closing a TKI.")
        return cleaned
