from django.db import models
from users.models import User
import uuid



class WorkoutCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Workout Categories'


    def __str__(self):
        return self.name


class Exercise(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    muscle_group = models.JSONField(default=list, blank=True)
    equipment = models.JSONField(default=list)
    image = models.ImageField(upload_to='media/exercises/', blank=True, null=True)
    video = models.FileField(upload_to='media/exercises/videos/', blank=True, null=True)
    instructions = models.TextField(blank=True)
    DIFFICULTY = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    difficulty_level = models.CharField(max_length=50, choices=DIFFICULTY, default='beginner')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
 
    def __str__(self):
        return self.name


class Workout(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    DIFFICULTY = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    difficulty_level = models.CharField(max_length=50, choices=DIFFICULTY, default='beginner')
    duration_minutes = models.PositiveIntegerField()
    calories_estimated = models.PositiveBigIntegerField(default=0)
    image = models.ImageField(upload_to='media/workouts/', blank=True, null=True)
    is_premium = models.BooleanField(default=False)
    is_training_of_the_day = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_workouts')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(WorkoutCategory, on_delete=models.SET_NULL, null=True, related_name='workouts')


    class Meta:
        ordering = ['-created_at']


    def __str__(self):
        return f"{self.title} - {self.created_by}"

    
class WorkoutExercise(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='workout_exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.PositiveIntegerField(default=3)
    reps = models.PositiveIntegerField(blank=True, null=True)
    duration_seconds = models.PositiveIntegerField(blank=True, null=True)
    rest_seconds = models.PositiveIntegerField(default=60)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


    def __str__(self):
        return f"{self.workout.title} - {self.exercise.name} (Set: {self.sets}, Reps: {self.reps})"


class CustomRoutine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_routines')
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.nickname}"


class CustomRoutineExercise(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    custom_routine = models.ForeignKey(CustomRoutine, on_delete=models.CASCADE, related_name='custom_routine_exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.PositiveIntegerField(default=3)
    reps = models.PositiveIntegerField(blank=True, null=True)
    duration_seconds = models.PositiveIntegerField(blank=True, null=True)
    rest_seconds = models.PositiveIntegerField(default=60)
    order = models.PositiveIntegerField(default=0)
    round_number = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['round_number', 'order']


    def __str__(self):
        return f"{self.custom_routine.title} - {self.exercise.name} (Set: {self.sets}, Reps: {self.reps})"


class UserWorkoutLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_logs')
    workout = models.ForeignKey(Workout, on_delete=models.SET_NULL, null=True, blank=True)
    custom_routine = models.ForeignKey(CustomRoutine, on_delete=models.SET_NULL, null=True, blank=True)
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(blank=True, null=True)
    duration_seconds = models.PositiveIntegerField(blank=True, null=True)
    calories_burned = models.FloatField(blank=True, null=True)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-started_at']


    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.workout and not self.custom_routine:
            raise ValidationError("Workout yoki CustomRoutine dan biri majburiy.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


    def __str__(self):
        if self.workout:
            name = self.workout.title
        elif self.custom_routine:
            name = self.custom_routine.title
        else:
            name = 'Unknown'
        return f"{self.user.nickname} - {name} on {self.started_at.date()}"


class ExerciseLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_workout_log = models.ForeignKey(UserWorkoutLog, on_delete=models.CASCADE, related_name='exercise_logs')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets_number = models.PositiveIntegerField()
    reps = models.PositiveIntegerField(blank=True, null=True)
    weight_used = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    duration_seconds = models.PositiveIntegerField(blank=True, null=True)
    completed = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user_workout_log.user.nickname} - {self.exercise.name if self.exercise else 'Unknown Exercise'} Log"



class FavoriteWorkout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_workouts')
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'workout')

    def __str__(self):
        return f"{self.user.nickname} - {self.workout.title} (Favorite)"