import mimetypes
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import SuspiciousFileOperation
from django.contrib.staticfiles import finders
from django.core.mail import send_mail
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .forms import BookOrderForm
from .models import Book, BookCategory, BookOrder


def library(request):
    books = Book.objects.filter(is_published=True).select_related("category")
    categories = BookCategory.objects.filter(books__is_published=True).distinct().order_by("name")
    uncategorized_count = books.filter(category__isnull=True).count()
    return render(request, "books/library.html", {"books": books, "categories": categories, "uncategorized_count": uncategorized_count})


def book_detail(request, slug):
    book = get_object_or_404(Book, slug=slug, is_published=True)
    return render(request, "books/detail.html", {
        "book": book,
        "bkash_number": getattr(settings, "BOOKSTORE_BKASH_NUMBER", ""),
    })


@require_http_methods(["GET", "POST"])
def place_order(request, slug):
    book = get_object_or_404(Book, slug=slug, is_published=True)
    if request.method == "POST":
        form = BookOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.book = book
            order.amount = book.price
            try:
                order.save()
            except Exception:
                form.add_error("transaction_id", "This Transaction ID has already been submitted. Please check it.")
            else:
                return redirect("books:order_status", code=order.order_code)
    else:
        form = BookOrderForm()
    return render(request, "books/order.html", {"book": book, "form": form, "bkash_number": getattr(settings, "BOOKSTORE_BKASH_NUMBER", "")})


def order_status(request, code):
    order = get_object_or_404(BookOrder.objects.select_related("book"), order_code=code)
    return render(request, "books/order_status.html", {"order": order})


def preview_pdf(request, slug):
    book = get_object_or_404(Book, slug=slug, is_published=True)

    # Prefer the Admin-uploaded file when it is available. Render's local
    # filesystem is ephemeral, so also support a preview committed to GitHub
    # at static/books/previews/<book-slug>.pdf.
    preview_file = None
    if book.preview_pdf:
        try:
            preview_file = book.preview_pdf.open("rb")
        except (OSError, ValueError, SuspiciousFileOperation):
            preview_file = None

    if preview_file is None:
        preview_path = finders.find(f"books/previews/{book.slug}.pdf")
        if not preview_path:
            raise Http404("Preview PDF is unavailable. Upload the first-five-page PDF to static/books/previews using the exact book slug as its filename.")
        try:
            preview_file = open(preview_path, "rb")
        except OSError:
            raise Http404("Preview PDF could not be opened.")

    return FileResponse(
        preview_file,
        content_type="application/pdf",
        filename=f"{book.slug}-preview.pdf",
    )


def download_pdf(request, code):
    order = get_object_or_404(BookOrder.objects.select_related("book"), order_code=code)
    if order.status != BookOrder.Status.APPROVED:
        raise Http404("This download is not available until payment is approved.")
    if not order.book.full_pdf:
        raise Http404("Book file is unavailable.")
    try:
        full_file = order.book.full_pdf.open("rb")
    except (OSError, ValueError, SuspiciousFileOperation):
        raise Http404("Book file is unavailable on the server. Please contact the administrator.")
    return FileResponse(full_file, as_attachment=False, filename=f"{order.book.slug}.pdf", content_type="application/pdf")
