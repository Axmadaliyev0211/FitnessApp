from django.db import models
import uuid
from users.models import User


class Article(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=250)
    content = models.TextField()
    image = models.ImageField(upload_to='media/articles/', blank=True, null=True)
    author = models.CharField(max_length=250, null=True, blank=True)
    CATEGORY_CHOICES = [
    ('nutrition', 'Nutrition'),
    ('workout', 'Workout'),
    ('motivation', 'Motivation'),
    ('health', 'Health'),
    ('lifestyle', 'Lifestyle'),
    ('mental_health', 'Mental Health'),
    ('supplements', 'Supplements'),
    ('other', 'Other'),]
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_at']

 
    def __str__(self):
        return self.title


class FavoriteArticle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_articles')
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article')

    def __str__(self):
        return f"{self.user.username} favorited {self.article.title}"



