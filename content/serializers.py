from rest_framework import serializers
from .models import Article, FavoriteArticle


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'


class FavoriteArticleSerializer(serializers.ModelSerializer):
    article = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.all()
    )
    article_detail = ArticleSerializer(source='article', read_only=True)

    class Meta:
        model = FavoriteArticle
        fields = ('id', 'article', 'article_detail', 'added_at')
        read_only_fields = ('id', 'added_at')
 