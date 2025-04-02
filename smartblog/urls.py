# projenizin_adi/urls.py (Ana urls.py)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="SmartBlog API",
      default_version='v1',
      description="SmartBlog REST API documentation",
      # Bu alanları kendi projenize göre güncelleyin
      terms_of_service="https://www.example.com/policies/terms/",
      contact=openapi.Contact(email="contact@example.com"),
      license=openapi.License(name="MIT License"), # Projenizin lisansını belirtin
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Blog uygulamasının web view'larını ana dizine bağlıyoruz
    path('', include('blog.urls')),
    # Blog uygulamasının API view'larını /api/ altına bağlıyoruz
    path('api/', include('blog.api.urls')), # blog.api.urls dosyasındaki düzeltme önemli

    # Swagger ve Redoc URL'leri
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Geliştirme ortamında (DEBUG=True) medya dosyalarını sunmak için
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Geliştirme ortamında statik dosyaları da sunmak genellikle faydalıdır
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# NOT: Production ortamında medya ve statik dosyalar web sunucusu (Nginx vb.)
# tarafından sunulmalıdır. Bu static() yardımcıları production için değildir.