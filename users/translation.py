from modeltranslation.translator import register, TranslationOptions
from .models import UserGoal

@register(UserGoal)
class UserGoalTranslationOptions(TranslationOptions):
    fields = ('title',)