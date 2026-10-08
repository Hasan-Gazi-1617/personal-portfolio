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
            "tki_id", "client_id", "opened_at", "status", "dependency",
            "higher_level_noc", "noc_field_visit_done", "field_support_engineer", "field_support_done", "attention", "remarks",
            "category", "priority", "isp_related", "complaint", "assigned_engineer",
            "findings", "troubleshooting", "resolution",
        )
        widgets = {
            "opened_at": DateTimeLocalInput(format="%Y-%m-%dT%H:%M"),
            "complaint": forms.Textarea(attrs={"rows": 4}),
            "findings": forms.Textarea(attrs={"rows": 3}),
            "troubleshooting": forms.Textarea(attrs={"rows": 3}),
            "resolution": forms.Textarea(attrs={"rows": 3}),
            "remarks": forms.Textarea(attrs={"rows": 3, "placeholder": "Latest update / last comment"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["opened_at"].input_formats = ("%Y-%m-%dT%H:%M",)
        # TKI workflow uses only Pending and TKI Solved in the entry forms.
        self.fields["status"].choices = (
            (ComplaintTicket.Status.PENDING, ComplaintTicket.Status.PENDING.label),
            (ComplaintTicket.Status.SOLVED, ComplaintTicket.Status.SOLVED.label),
        )
        # ISP is no longer an available dependency for new TKI entries.
        self.fields["dependency"].choices = tuple(
            choice for choice in ComplaintTicket.Dependency.choices
            if choice[0] != ComplaintTicket.Dependency.ISP
        )
        self.fields["assigned_engineer"].queryset = User.objects.filter(is_active=True, is_staff=False).order_by("first_name", "username")
        self.fields["assigned_engineer"].required = False

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("field_support_done") and not cleaned.get("field_support_engineer"):
            self.add_error("field_support_engineer", "Select the field engineer who completed the support.")
        if cleaned.get("noc_field_visit_done") and not cleaned.get("higher_level_noc"):
            self.add_error("higher_level_noc", "Select the NOC engineer who completed the field visit.")
        return cleaned


class EngineerTicketUpdateForm(forms.ModelForm):
    class Meta:
        model = ComplaintTicket
        fields = ("status", "dependency", "higher_level_noc", "noc_field_visit_done", "field_support_engineer", "field_support_done", "attention", "remarks", "findings", "troubleshooting", "resolution")
        widgets = {
            "findings": forms.Textarea(attrs={"rows": 3}),
            "troubleshooting": forms.Textarea(attrs={"rows": 4}),
            "resolution": forms.Textarea(attrs={"rows": 3}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("field_support_done") and not cleaned.get("field_support_engineer"):
            self.add_error("field_support_engineer", "Select the field engineer who completed the support.")
        if cleaned.get("noc_field_visit_done") and not cleaned.get("higher_level_noc"):
            self.add_error("higher_level_noc", "Select the NOC engineer who completed the field visit.")
        if cleaned.get("status") == ComplaintTicket.Status.SOLVED:
            if not cleaned.get("findings") or not cleaned.get("troubleshooting"):
                raise forms.ValidationError("Findings and troubleshooting are required before resolving or closing a TKI.")
        return cleaned
