from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from modeltranslation.admin import TranslationAdmin
from .models import User, UserGoal, UserSettings


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'nickname', 'full_name', 'is_premium', 'is_trainer', 'is_staff', 'is_active')
    list_filter = ('is_premium', 'is_trainer', 'is_staff', 'is_active', 'fitness_level', 'gender')
    search_fields = ('email', 'username', 'nickname', 'full_name', 'phone_number')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Shaxsiy ma’lumotlar', {
            'fields': (
                'nickname', 'full_name', 'phone_number', 'avatar',
                'gender', 'date_of_birth', 'height_cm', 'weight_kg',
                'fitness_level', 'primary_goal', 'fingerprint_enabled'
            )
        }),
        ('Huquqlar', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'is_premium', 'is_trainer',
                'groups', 'user_permissions'
            )
        }),
        ('Sanalar', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('last_login', 'date_joined', 'created_at', 'updated_at')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'full_name', 'password1', 'password2'),
        }),
    )


@admin.register(UserGoal)
class UserGoalAdmin(TranslationAdmin):
    list_display = ('user', 'title', 'goal_type', 'status', 'target_value', 'current_value', 'unit', 'start_date', 'end_date')
    list_filter = ('status', 'goal_type')
    search_fields = ('user__email', 'user__nickname', 'title')


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'notifications_enabled', 'sound_enabled', 'reminder_enabled', 'do_not_disturb_enabled')
    search_fields = ('user__email', 'user__nickname')