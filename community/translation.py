from modeltranslation.translator import register, TranslationOptions
from .models import Challenge, ForumCategory, ForumPost

@register(Challenge)
class ChallengeTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

@register(ForumCategory)
class ForumCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(ForumPost)
class ForumPostTranslationOptions(TranslationOptions):
    fields = ('title', 'content')