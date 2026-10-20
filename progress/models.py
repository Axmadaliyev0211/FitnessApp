from django.db import models
from users.models import User
import uuid


class ProgressEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_entries')
    date = models.DateField()
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    body_fat_percentage = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    chest_cm = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    waist_cm = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    hips_cm = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='media/progress_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ('user', 'date')


    def __str__(self):
        return f"Progress Entry for {self.user.username} on {self.date}"



class ActivityLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    date = models.DateField()
    steps = models.PositiveIntegerField(default=0)
    distance_km = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    calories_burned = models.PositiveIntegerField(default=0)
    active_minutes = models.PositiveIntegerField(default=0)
    heart_rate_avg = models.PositiveIntegerField(blank=True, null=True)
    ACTIVITY_SOURCE_CHOICES = [
        ('manual', 'Manual'),
        ('apple_health', 'Apple Health'),
        ('google_fit', 'Google Fit'),
        ('fitbit', 'Fitbit'),
        ('device', 'Device'),
        ('app', 'App'),
        ('other', 'Other'),
    ]
    source = models.CharField(max_length=20, choices=ACTIVITY_SOURCE_CHOICES, default='manual')
    created_at = models.DateTimeField(auto_now_add=True)

 
    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']


    def __str__(self):
        return f"Activity Log for {self.user.username} on {self.date}"



