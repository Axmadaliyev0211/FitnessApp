from .models import Notification

def create_notification(user, title, body, type='system', data=None):
    """
    type mumkin bo'lgan qiymatlar:
    'workout_reminder', 'article', 'water', 'goal', 'system', 'challenge'
    """
    return Notification.objects.create(
        user=user,
        title=title,
        body=body,
        type=type,
        data=data or {}
    )