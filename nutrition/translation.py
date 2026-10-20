from modeltranslation.translator import register, TranslationOptions
from .models import Recipe

@register(Recipe)
class RecipeTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'ingredients', 'preparation_steps')