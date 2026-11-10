from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("books", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="book",
            name="cover",
            field=models.ImageField(
                blank=True,
                help_text="Optional Admin upload. For a GitHub-managed cover, add static/images/books/<slug>.jpg (or .png, .webp, .jpeg).",
                upload_to="books/covers/",
            ),
        ),
        migrations.AlterField(
            model_name="book",
            name="preview_pdf",
            field=models.FileField(
                blank=True,
                help_text="Upload a PDF containing only the first five pages, or add static/books/previews/<slug>.pdf to GitHub.",
                upload_to="books/previews/",
            ),
        ),
        migrations.AlterField(
            model_name="book",
            name="full_pdf",
            field=models.FileField(
                help_text="Complete PDF. Served only after payment approval. Note: Render local uploads are temporary; use persistent private storage for production files.",
                upload_to="books/private/",
            ),
        ),
    ]
