
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('analytics/', include('site_insights.urls')),
    path('library/', include('books.urls')),
    path('', include('attendance.urls')),
    path('', include('bcs_exam.urls')),
    path('', include('portfolio.urls')),
]

