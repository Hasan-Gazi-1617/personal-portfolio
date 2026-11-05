import uuid
from django.core.validators import MinValueValidator
from django.db import models
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
    cover = models.ImageField(upload_to="books/covers/", blank=True)
    preview_pdf = models.FileField(upload_to="books/previews/", help_text="Upload a PDF containing only the first five pages.")
    full_pdf = models.FileField(upload_to="books/private/", help_text="Full PDF. Downloads are served through the protected view.")
    price = models.DecimalField(max_digits=9, decimal_places=2, validators=[MinValueValidator(1)])
    is_published = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title


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
