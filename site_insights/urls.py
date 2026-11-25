from django.urls import path
from . import views

app_name = 'site_insights'
urlpatterns = [
    path('', views.public_dashboard, name='public_dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('module/', views.track_module, name='track_module'),
    path('event/', views.track_event, name='track_event'),
]
