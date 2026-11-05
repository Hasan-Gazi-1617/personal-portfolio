from django.db import migrations, models
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name="BookCategory", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("name", models.CharField(max_length=100, unique=True)), ("slug", models.SlugField(max_length=110, unique=True))], options={"ordering": ("name",), "verbose_name_plural": "Book categories"}),
        migrations.CreateModel(name="Book", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("title", models.CharField(max_length=220)), ("slug", models.SlugField(max_length=240, unique=True)), ("author", models.CharField(blank=True, max_length=160)), ("description", models.TextField(blank=True)), ("cover", models.ImageField(blank=True, upload_to="books/covers/")), ("preview_pdf", models.FileField(help_text="Upload a PDF containing only the first five pages.", upload_to="books/previews/")), ("full_pdf", models.FileField(help_text="Full PDF. Downloads are served through the protected view.", upload_to="books/private/")), ("price", models.DecimalField(decimal_places=2, max_digits=9, validators=[django.core.validators.MinValueValidator(1)])), ("is_published", models.BooleanField(db_index=True, default=False)), ("created_at", models.DateTimeField(auto_now_add=True)), ("category", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="books", to="books.bookcategory"))], options={"ordering": ("-created_at",)}),
        migrations.CreateModel(name="BookOrder", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("order_code", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)), ("customer_name", models.CharField(max_length=120)), ("customer_email", models.EmailField(db_index=True, max_length=254)), ("customer_phone", models.CharField(max_length=20)), ("transaction_id", models.CharField(max_length=80, unique=True)), ("amount", models.DecimalField(decimal_places=2, max_digits=9)), ("status", models.CharField(choices=[("pending", "Pending verification"), ("approved", "Approved"), ("rejected", "Rejected")], db_index=True, default="pending", max_length=12)), ("admin_note", models.TextField(blank=True)), ("created_at", models.DateTimeField(default=django.utils.timezone.now)), ("verified_at", models.DateTimeField(blank=True, null=True)), ("book", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="orders", to="books.book"))], options={"ordering": ("-created_at",)}),
    ]
