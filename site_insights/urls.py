from django.urls import path
from . import views

app_name = 'site_insights'
urlpatterns = [
    path('subscribe/', views.subscribe, name='subscribe'),
    path('unsubscribe/<uuid:token>/', views.unsubscribe, name='unsubscribe'),
    path('event/', views.track_event, name='track_event'),
]
