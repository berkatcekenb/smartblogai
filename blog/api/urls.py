# blog/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Bu view'ların blog/api/views.py altında olduğunu varsayıyoruz
from .views import PostViewSet, CommentViewSet

router = DefaultRouter()

# Ana urls.py'de 'api/' ön eki zaten olduğu için buradaki ön ekler kaldırıldı.
router.register(r'posts', PostViewSet, basename='api-post') # 'api/' kaldırıldı
router.register(r'comments', CommentViewSet, basename='api-comment') # 'api/' kaldırıldı

urlpatterns = [
    path('', include(router.urls)),
]

# Not: Yukarıdaki router.register içindeki 'r' harfi (raw string)
# isteğe bağlıdır ama URL desenlerinde kullanmak iyi bir pratiktir.