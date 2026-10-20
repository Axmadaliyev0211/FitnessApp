from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import (
    ForumCategory, ForumPost, ForumComment,
    Challenge, ChallengeRound, ChallengeExercise,
    UserChallenge, PostLike
)


@admin.register(ForumCategory)
class ForumCategoryAdmin(TranslationAdmin):
    list_display = ('name', 'slug', 'order')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ForumPost)
class ForumPostAdmin(TranslationAdmin):
    list_display = ('title', 'user', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('title', 'user__email', 'user__nickname')


@admin.register(ForumComment)
class ForumCommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at')
    search_fields = ('content', 'user__email')


class ChallengeExerciseInline(admin.TabularInline):
    model = ChallengeExercise
    extra = 1


class ChallengeRoundInline(admin.TabularInline):
    model = ChallengeRound
    extra = 1
    show_change_link = True


@admin.register(Challenge)
class ChallengeAdmin(TranslationAdmin):
    list_display = ('title', 'difficulty_level', 'is_weekly', 'is_active', 'start_date', 'end_date')
    list_filter = ('difficulty_level', 'is_weekly', 'is_active')
    search_fields = ('title',)
    inlines = [ChallengeRoundInline]


@admin.register(ChallengeRound)
class ChallengeRoundAdmin(admin.ModelAdmin):
    list_display = ('title', 'challenge', 'order')
    inlines = [ChallengeExerciseInline]


@admin.register(UserChallenge)
class UserChallengeAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'status', 'start_date', 'end_date', 'total_calories', 'total_duration')
    list_filter = ('status',)
    search_fields = ('user__email', 'challenge__title')


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    search_fields = ('user__email', 'post__title')