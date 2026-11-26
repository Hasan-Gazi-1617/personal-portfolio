from django.db import migrations, models
import uuid

class Migration(migrations.Migration):
    dependencies = [("portfolio", "0009_ielts_learning_hub")]
    operations = [migrations.AddField(model_name="ieltsassignmentsubmission", name="receipt_code", field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True))]
