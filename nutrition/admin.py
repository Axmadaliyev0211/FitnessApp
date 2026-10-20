from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import Recipe, MealPlanPreference, GeneratedMealPlan, MealLog, FavoriteRecipe


@admin.register(Recipe)
class RecipeAdmin(TranslationAdmin):
    list_display = ('title', 'meal_type', 'calories', 'prep_time_minutes', 'is_recipe_of_the_day', 'is_active')
    list_filter = ('meal_type', 'is_recipe_of_the_day', 'is_active')
    search_fields = ('title',)


@admin.register(MealPlanPreference)
class MealPlanPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'caloric_goal', 'cooking_time_preference', 'number_of_servings', 'created_at')
    search_fields = ('user__email', 'user__nickname')


@admin.register(GeneratedMealPlan)
class GeneratedMealPlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'created_at')
    search_fields = ('user__email', 'user__nickname')
    filter_horizontal = ('recipes',)


@admin.register(MealLog)
class MealLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'meal_type', 'quantity', 'logged_at')
    list_filter = ('meal_type',)
    search_fields = ('user__email', 'recipe__title')


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'created_at')
    search_fields = ('user__email', 'recipe__title')