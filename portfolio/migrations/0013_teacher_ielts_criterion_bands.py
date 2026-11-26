from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio", "0012_remove_ielts_assignment_ai_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="ieltsassignmentsubmission",
            name="task_response_band",
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=2, null=True),
        ),
        migrations.AddField(
            model_name="ieltsassignmentsubmission",
            name="coherence_cohesion_band",
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=2, null=True),
        ),
        migrations.AddField(
            model_name="ieltsassignmentsubmission",
            name="lexical_resource_band",
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=2, null=True),
        ),
        migrations.AddField(
            model_name="ieltsassignmentsubmission",
            name="grammatical_range_band",
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=2, null=True),
        ),
    ]
