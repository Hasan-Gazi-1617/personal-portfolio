
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('library/', include('books.urls')),
    path('', include('portfolio.urls')),
]

if settings.DEBUG and not all((settings.R2_ACCESS_KEY_ID, settings.R2_SECRET_ACCESS_KEY, settings.R2_BUCKET_NAME, settings.R2_ENDPOINT_URL)):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
