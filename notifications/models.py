from django.db import models
import uuid
from users.models import User


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    body = models.TextField()
    TYPE_CHOICES = [
        ('workout_reminder', 'Workout Reminder'),
        ('system', 'System'),
        ('challenge', 'Challenge'),
        ('article', 'Article'),
        ('water', 'Water'),
        ('goal', 'Goal'),
    ]

    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='system')
    is_read = models.BooleanField(default=False)
    data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"

 
