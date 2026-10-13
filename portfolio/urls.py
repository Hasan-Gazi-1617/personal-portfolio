from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("owner/olt-monitoring/", views.olt_monitoring_dashboard, name="olt_monitoring_dashboard"),
    path("api/olt/ingest/", views.olt_ingest, name="olt_ingest"),
    path("projects/mikrotik-config-generator/", views.mikrotik_generator, name="mikrotik_generator"),
    path("projects/algorithm-visual-studio/", views.algorithm_studio, name="algorithm_studio"),
    path("owner-login/", views.owner_login, name="owner_login"),
    path("owner-logout/", views.owner_logout, name="owner_logout"),
]
