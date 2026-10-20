from modeltranslation.translator import register, TranslationOptions
from .models import WorkoutCategory, Workout, Exercise

@register(WorkoutCategory)
class WorkoutCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Workout)
class WorkoutTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

@register(Exercise)
class ExerciseTranslationOptions(TranslationOptions):
    fields = ('name', 'description')