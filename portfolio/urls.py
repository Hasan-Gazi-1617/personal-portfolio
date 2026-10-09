from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("projects/mikrotik-config-generator/", views.mikrotik_generator, name="mikrotik_generator"),
    path("projects/algorithm-visual-studio/", views.algorithm_studio, name="algorithm_studio"),
    path("tki/", views.tki_fresh_dashboard, name="tki_dashboard"),
    path("tki/export/", views.tki_export_xlsx, name="tki_export_xlsx"),
    path("tki/delete-month/", views.tki_delete_month, name="tki_delete_month"),
    path("tki/delete-range/", views.tki_delete_range, name="tki_delete_range"),
    path("tki/import-solved/", views.tki_import_solved, name="tki_import_solved"),
    path("tki/new/", views.tki_create, name="tki_create"),
    path("tki/<int:pk>/", views.tki_detail, name="tki_detail"),
    path("tki/<int:pk>/update/", views.tki_update, name="tki_update"),
    path("tki/<int:pk>/admin-edit/", views.tki_admin_edit, name="tki_admin_edit"),
    path("owner-login/", views.owner_login, name="owner_login"),
    path("owner-logout/", views.owner_logout, name="owner_logout"),
]
