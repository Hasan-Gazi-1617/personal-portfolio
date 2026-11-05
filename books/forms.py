from django import forms
from .models import BookOrder


class BookOrderForm(forms.ModelForm):
    class Meta:
        model = BookOrder
        fields = ("customer_name", "customer_email", "customer_phone", "transaction_id")
        widgets = {
            "customer_name": forms.TextInput(attrs={"placeholder": "Your full name"}),
            "customer_email": forms.EmailInput(attrs={"placeholder": "name@example.com"}),
            "customer_phone": forms.TextInput(attrs={"placeholder": "01XXXXXXXXX"}),
            "transaction_id": forms.TextInput(attrs={"placeholder": "bKash Transaction ID"}),
        }
