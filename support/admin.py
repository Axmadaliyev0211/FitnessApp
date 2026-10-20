from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import FAQ, SupportMessage


@admin.register(FAQ)
class FAQAdmin(TranslationAdmin):
    list_display = ('question', 'category', 'order')
    list_filter = ('category',)
    search_fields = ('question',)
    ordering = ('order',)


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'message_short', 'is_from_user', 'is_read', 'created_at')
    list_filter = ('is_from_user', 'is_read')
    search_fields = ('user__email', 'user__nickname', 'message')

    @admin.display(description='Message')
    def message_short(self, obj):
        return obj.message[:50]