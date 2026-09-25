from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("projects/mikrotik-config-generator/", views.mikrotik_generator, name="mikrotik_generator"),
    path("owner-login/", views.owner_login, name="owner_login"),
    path("owner-logout/", views.owner_logout, name="owner_logout"),
]
