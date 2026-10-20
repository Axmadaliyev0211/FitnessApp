from modeltranslation.translator import register, TranslationOptions
from .models import ProgressEntry, ActivityLog

@register(ProgressEntry)
class ProgressEntryTranslationOptions(TranslationOptions):
    fields = ('notes',)          # agar notes maydoni bo‘lsa

# @register(ActivityLog)
# class ActivityLogTranslationOptions(TranslationOptions):
#     fields = ('notes',)          # agar notes maydoni bo‘lsa