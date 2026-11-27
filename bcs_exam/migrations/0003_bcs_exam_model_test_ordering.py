from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("bcs_exam", "0002_exam_number_and_teacher_review"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="bcsexam",
            options={"ordering": ("model_test_number", "-created_at")},
        ),
    ]
