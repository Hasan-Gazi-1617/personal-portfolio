from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("projects/mikrotik-config-generator/", views.mikrotik_generator, name="mikrotik_generator"),
    path("projects/algorithm-visual-studio/", views.algorithm_studio, name="algorithm_studio"),
    path("tki/login/", views.TkiLoginView.as_view(), name="tki_login"),
    path("tki/logout/", views.TkiLogoutView.as_view(), name="tki_logout"),
    path("tki/", views.tki_dashboard, name="tki_dashboard"),
    path("tki/new/", views.tki_create, name="tki_create"),
    path("tki/<int:pk>/", views.tki_detail, name="tki_detail"),
    path("tki/<int:pk>/claim/", views.tki_claim, name="tki_claim"),
    path("tki/<int:pk>/update/", views.tki_update, name="tki_update"),
    path("tki/<int:pk>/admin-edit/", views.tki_admin_edit, name="tki_admin_edit"),
    path("owner-login/", views.owner_login, name="owner_login"),
    path("owner-logout/", views.owner_logout, name="owner_logout"),
]
