from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("books", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="book",
            name="preview_pdf",
            field=models.FileField(
                blank=True,
                help_text="Upload a PDF containing only the first five pages, or add static/books/previews/<slug>.pdf to GitHub.",
                upload_to="books/previews/",
            ),
        ),
    ]
