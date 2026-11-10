import uuid
from pathlib import Path

from django.conf import settings
from django.core.validators import MinValueValidator
from django.contrib.staticfiles import finders
from django.db import models
from django.templatetags.static import static
from django.utils import timezone


class BookCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Book categories"

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=240, unique=True)
    author = models.CharField(max_length=160, blank=True)
    category = models.ForeignKey(BookCategory, null=True, blank=True, on_delete=models.SET_NULL, related_name="books")
    description = models.TextField(blank=True)
    cover = models.ImageField(
        upload_to="books/covers/",
        blank=True,
        help_text="Optional Admin upload. For a GitHub-managed cover, add static/images/books/<slug>.jpg (or .png, .webp, .jpeg).",
    )
    preview_pdf = models.FileField(
        upload_to="books/previews/",
        blank=True,
        help_text="Upload a PDF containing only the first five pages, or add static/books/previews/<slug>.pdf to GitHub.",
    )
    full_pdf = models.FileField(
        upload_to="books/private/",
        help_text="Complete PDF. Served only after payment approval. Note: Render local uploads are temporary; use persistent private storage for production files.",
    )
    price = models.DecimalField(max_digits=9, decimal_places=2, validators=[MinValueValidator(1)])
    is_published = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title

    @property
    def cover_url(self):
        if self.cover:
            try:
                if self.cover.storage.exists(self.cover.name):
                    return self.cover.url
            except (OSError, ValueError):
                pass

        static_dir = Path(settings.BASE_DIR) / "static" / "images" / "books"
        for extension in ("webp", "jpg", "jpeg", "png"):
            filename = f"{self.slug}.{extension}"
            if (static_dir / filename).is_file():
                return static(f"images/books/{filename}")
        return ""

    @property
    def preview_available(self):
        if self.preview_pdf:
            try:
                if self.preview_pdf.storage.exists(self.preview_pdf.name):
                    return True
            except (OSError, ValueError):
                pass

        return bool(finders.find(f"books/previews/{self.slug}.pdf"))


class BookOrder(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending verification"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    order_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name="orders")
    customer_name = models.CharField(max_length=120)
    customer_email = models.EmailField(db_index=True)
    customer_phone = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=80, unique=True)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING, db_index=True)
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.order_code} - {self.book.title}"
