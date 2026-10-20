from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import ProgressEntry, ActivityLog


@admin.register(ProgressEntry)
class ProgressEntryAdmin(TranslationAdmin):
    list_display = ('user', 'date', 'weight_kg', 'body_fat_percentage', 'chest_cm', 'waist_cm', 'hips_cm')
    list_filter = ('date',)
    search_fields = ('user__email', 'user__nickname')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'steps', 'distance_km', 'calories_burned', 'active_minutes', 'heart_rate_avg', 'source')
    list_filter = ('source', 'date')
    search_fields = ('user__email', 'user__nickname')