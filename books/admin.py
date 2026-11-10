from django.contrib import admin
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from .models import Book, BookCategory, BookOrder


@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "price", "is_published", "created_at")
    list_filter = ("is_published", "category")
    search_fields = ("title", "author")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        ("Book information", {
            "fields": ("title", "slug", "author", "category", "description", "price", "is_published"),
        }),
        ("Book files", {
            "fields": ("cover", "preview_pdf", "full_pdf"),
            "description": (
                "Cover and preview can be committed to GitHub static folders using the book slug. "
                "The full PDF must remain in private persistent storage and must never be placed in a public repository."
            ),
        }),
    )


@admin.action(description="Approve selected orders after verifying bKash payment")
def approve_orders(modeladmin, request, queryset):
    pending = list(queryset.filter(status=BookOrder.Status.PENDING).select_related("book"))
    for order in pending:
        order.status = BookOrder.Status.APPROVED
        order.verified_at = timezone.now()
        order.save(update_fields=("status", "verified_at"))
        download_url = f"{settings.BOOKSTORE_SITE_URL}{reverse('books:download', args=[order.order_code])}"
        send_mail(
            subject=f"Your book is ready: {order.book.title}",
            message=f"Hello {order.customer_name},\n\nYour bKash payment has been verified. Download your book here:\n{download_url}\n\nThank you.",
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            recipient_list=[order.customer_email],
            fail_silently=True,
        )


@admin.action(description="Reject selected pending orders")
def reject_orders(modeladmin, request, queryset):
    queryset.filter(status=BookOrder.Status.PENDING).update(status=BookOrder.Status.REJECTED)


@admin.register(BookOrder)
class BookOrderAdmin(admin.ModelAdmin):
    list_display = ("order_code", "book", "customer_name", "customer_email", "transaction_id", "amount", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order_code", "customer_name", "customer_email", "transaction_id")
    readonly_fields = ("order_code", "book", "customer_name", "customer_email", "customer_phone", "transaction_id", "amount", "created_at", "verified_at")
    actions = (approve_orders, reject_orders)
