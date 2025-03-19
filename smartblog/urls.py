from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin URL'i ilk sırada
    path('', include('blog.urls')),
    path('api/', include('blog.api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
