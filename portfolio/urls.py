from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("owner-login/", views.owner_login, name="owner_login"),
    path("owner-logout/", views.owner_logout, name="owner_logout"),
    path("owner/olt-monitor/", views.olt_dashboard, name="olt_dashboard"),
    path("owner/api/olt/status/", views.olt_status_api, name="olt_status_api"),
    path("owner/api/olt/ingest/", views.olt_ingest, name="olt_ingest"),
]
