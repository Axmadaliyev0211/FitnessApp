from django.db import models
import uuid
from users.models import User


class FAQ(models.Model):
    question = models.CharField(max_length=300)
    answer = models.TextField()
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('nutrition', 'Nutrition'),
        ('workouts', 'Workouts'),
        ('progress', 'Progress'),
        ('notifications', 'Notifications'),
    ]
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='general')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'


    def __str__(self):
        return self.question


class SupportMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_messages')
    message = models.TextField()
    is_from_user = models.BooleanField(default=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
 

    def __str__(self):
        return f"{self.user} - {self.message[:30]}"