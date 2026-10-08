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
            "higher_level_noc", "field_support_engineer", "attention", "remarks",
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
        self.fields["assigned_engineer"].queryset = User.objects.filter(is_active=True, is_staff=False).order_by("first_name", "username")
        self.fields["assigned_engineer"].required = False


class EngineerTicketUpdateForm(forms.ModelForm):
    class Meta:
        model = ComplaintTicket
        fields = ("status", "dependency", "higher_level_noc", "field_support_engineer", "attention", "remarks", "findings", "troubleshooting", "resolution")
        widgets = {
            "findings": forms.Textarea(attrs={"rows": 3}),
            "troubleshooting": forms.Textarea(attrs={"rows": 4}),
            "resolution": forms.Textarea(attrs={"rows": 3}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("status") == ComplaintTicket.Status.SOLVED:
            if not cleaned.get("findings") or not cleaned.get("troubleshooting"):
                raise forms.ValidationError("Findings and troubleshooting are required before resolving or closing a TKI.")
        return cleaned
