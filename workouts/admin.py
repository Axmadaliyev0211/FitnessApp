from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import (
    WorkoutCategory, Exercise, Workout, WorkoutExercise,
    CustomRoutine, CustomRoutineExercise, UserWorkoutLog,
    ExerciseLog, FavoriteWorkout
)


@admin.register(WorkoutCategory)
class WorkoutCategoryAdmin(TranslationAdmin):
    list_display = ('name', 'slug', 'order')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Exercise)
class ExerciseAdmin(TranslationAdmin):
    list_display = ('name', 'muscle_group', 'difficulty_level', 'is_active')
    list_filter = ('muscle_group', 'difficulty_level', 'is_active')
    search_fields = ('name',)


class WorkoutExerciseInline(admin.TabularInline):
    model = WorkoutExercise
    extra = 1
    autocomplete_fields = ('exercise',)


@admin.register(Workout)
class WorkoutAdmin(TranslationAdmin):
    list_display = (
        'title', 'category', 'difficulty_level', 'duration_minutes',
        'calories_estimated', 'is_premium', 'is_training_of_the_day', 'is_active'
    )
    list_filter = ('difficulty_level', 'is_premium', 'is_training_of_the_day', 'is_active', 'category')
    search_fields = ('title',)
    autocomplete_fields = ('category',)
    inlines = [WorkoutExerciseInline]


class CustomRoutineExerciseInline(admin.TabularInline):
    model = CustomRoutineExercise
    extra = 1
    autocomplete_fields = ('exercise',)


@admin.register(CustomRoutine)
class CustomRoutineAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')
    search_fields = ('title', 'user__email', 'user__nickname')
    inlines = [CustomRoutineExerciseInline]


class ExerciseLogInline(admin.TabularInline):
    model = ExerciseLog
    extra = 0
    autocomplete_fields = ('exercise',)


@admin.register(UserWorkoutLog)
class UserWorkoutLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'workout', 'custom_routine', 'started_at', 'completed_at', 'duration_seconds', 'calories_burned', 'rating')
    list_filter = ('rating',)
    search_fields = ('user__email', 'user__nickname')
    inlines = [ExerciseLogInline]


@admin.register(FavoriteWorkout)
class FavoriteWorkoutAdmin(admin.ModelAdmin):
    list_display = ('user', 'workout', 'added_at')
    search_fields = ('user__email', 'workout__title')