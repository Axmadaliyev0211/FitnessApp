from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ArticleViewSet, FavoriteArticleViewSet

router = DefaultRouter()
router.register('articles', ArticleViewSet, basename='articles')
router.register('favorites', FavoriteArticleViewSet, basename='favorite-articles')

urlpatterns = [
    path('', include(router.urls)),
]