from django.urls import path
from . import views

app_name = "books"
urlpatterns = [
    path("", views.library, name="library"),
    path("book/<slug:slug>/", views.book_detail, name="detail"),
    path("book/<slug:slug>/preview/", views.preview_pdf, name="preview"),
    path("book/<slug:slug>/order/", views.place_order, name="order"),
    path("order/<uuid:code>/", views.order_status, name="order_status"),
    path("download/<uuid:code>/", views.download_pdf, name="download"),
]
