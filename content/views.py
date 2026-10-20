from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from .models import Article, FavoriteArticle
from .serializers import ArticleSerializer, FavoriteArticleSerializer
from core.permissions import IsOwner, IsAdminOrReadOnly
from core.language import set_language_from_user

class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        set_language_from_user(request)


    def get_queryset(self):
        return Article.objects.filter(published_at__isnull=False).order_by('-published_at')


class FavoriteArticleViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteArticleSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        return FavoriteArticle.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

