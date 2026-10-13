"""Retain the historical migration number without recreating retired seed tickets.

The legacy TKI seed records were intentionally removed so deleted/retired records
would not reappear on fresh deployments. Existing databases that already applied
this migration are unaffected; fresh databases should start with no legacy seed
tickets and operators can import current solved records through the private TSV
workflow.
"""
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("portfolio", "0002_complaintticket_attention_complaintticket_dependency_and_more"),
    ]
    operations = []
