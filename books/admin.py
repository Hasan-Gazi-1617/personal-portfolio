from django.contrib import admin
from django.utils import timezone
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


@admin.action(description="Approve selected orders after verifying bKash payment")
def approve_orders(modeladmin, request, queryset):
    queryset.filter(status=BookOrder.Status.PENDING).update(status=BookOrder.Status.APPROVED, verified_at=timezone.now())


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
