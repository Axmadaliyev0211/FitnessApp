from rest_framework import serializers
from .models import Recipe, MealPlanPreference, GeneratedMealPlan, MealLog, FavoriteRecipe


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id', 'title', 'description', 'image', 'video',
            'calories', 'protein', 'carbs', 'fat', 'prep_time_minutes',
            'meal_type', 'ingredients', 'preparation_steps',
            'is_recipe_of_the_day', 'is_active', 'created_at',
        )

class MealPlanPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealPlanPreference
        fields = (
            'dietary_preferences', 'allergies', 'meal_types',
            'caloric_goal', 'cooking_time_preference', 'number_of_servings'
        )
 

class GeneratedMealPlanSerializer(serializers.ModelSerializer):
    recipes = RecipeSerializer(many=True, read_only=True)

    class Meta:
        model = GeneratedMealPlan
        fields = ('id', 'date', 'recipes', 'created_at')
 


class MealLogSerializer(serializers.ModelSerializer):
    recipe_detail = RecipeSerializer(source='recipe', read_only=True)
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = MealLog
        fields = (
            'id', 'recipe', 'recipe_detail', 'meal_type',
            'quantity', 'logged_at', 'created_at'
        )
        read_only_fields = ('id', 'created_at')



class FavoriteRecipeSerializer(serializers.ModelSerializer):
    recipe_detail = RecipeSerializer(source='recipe', read_only=True)
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = FavoriteRecipe
        fields = ('id', 'recipe', 'recipe_detail', 'created_at')
        read_only_fields = ('id', 'created_at')


    def validate_recipe(self, value):
        user = self.context['request'].user
        if FavoriteRecipe.objects.filter(user=user, recipe=value).exists():
            raise serializers.ValidationError("Bu retsept allaqachon sevimlilarda.")
        return value
