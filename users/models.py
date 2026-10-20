from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid




class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nickname = models.CharField(max_length=50, blank=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='media/avatars/', blank=True, null=True)
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    height_cm = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    FITNESS_LEVEL = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    fitness_level = models.CharField(max_length=50, choices=FITNESS_LEVEL, default='beginner')
    GOAL_CHOICES = [
        ('lose_weight', 'Lose Weight'),
        ('gain_weight', 'Gain Weight'),
        ('muscle_mass_gain', 'Muscle Mass Gain'),
        ('shape_body', 'Shape Body'),
        ('others', 'Others'),
    ]
    primary_goal = models.CharField(max_length=50, choices=GOAL_CHOICES, default='others')
    is_premium = models.BooleanField(default=False)
    is_trainer = models.BooleanField(default=False)
    fingerprint_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'full_name']
 
    def __str__(self):
        return self.nickname


class UserGoal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    GOAL_TYPE_CHOICES = [
        ('lose_weight', 'Lose Weight'),
        ('gain_weight', 'Gain Weight'),
        ('muscle_mass_gain', 'Muscle Mass Gain'),
        ('shape_body', 'Shape Body'),
        ('others', 'Others'),
    ]
    goal_type = models.CharField(max_length=50, choices=GOAL_TYPE_CHOICES)
    title = models.CharField(max_length=100)
    target_value = models.DecimalField(max_digits=10, decimal_places=2)
    current_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    UNIT_CHOICES = [
        ('kg', 'kg'),
        ('lbs', 'lbs'),
        ('cm', 'cm'),
        ('inches', 'inches'),
        ('minutes', 'minutes'),
        ('reps', 'reps'),
    ]
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'User Goal'
        verbose_name_plural = 'User Goals'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.nickname} - {self.title}"


class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    notifications_enabled = models.BooleanField(default=True)
    sound_enabled = models.BooleanField(default=True)
    do_not_disturb_enabled = models.BooleanField(default=False)
    vibrate_enabled = models.BooleanField(default=True)
    lock_screen_enabled = models.BooleanField(default=True)
    reminder_enabled = models.BooleanField(default=True)



    LANGUAGE_CHOICES = [
        ('uz', 'O‘zbekcha'),
        ('en', 'English'),
        ('ru', 'Русский'),
    ]
    language = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        default='uz'
    )

    def __str__(self):
        return f"{self.user.nickname} Settings"



