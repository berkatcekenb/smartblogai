from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, CommentViewSet

router = DefaultRouter()
# URL prefix'lerini değiştiriyoruz
router.register('api/posts', PostViewSet, basename='api-post')
router.register('api/comments', CommentViewSet, basename='api-comment')

urlpatterns = [
    path('', include(router.urls)),
]
