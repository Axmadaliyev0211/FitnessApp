from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import Article, FavoriteArticle


@admin.register(Article)
class ArticleAdmin(TranslationAdmin):
    list_display = ('title', 'author', 'category', 'is_featured', 'published_at', 'created_at')
    list_filter = ('category', 'is_featured')
    search_fields = ('title', 'author')


@admin.register(FavoriteArticle)
class FavoriteArticleAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'added_at')
    search_fields = ('user__email', 'article__title')