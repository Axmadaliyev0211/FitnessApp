from django.db import models
from users.models import User
import uuid


class Recipe(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='media/recipes/', blank=True, null=True)
    video = models.FileField(upload_to='media/recipes/', blank=True, null=True)
    calories = models.PositiveBigIntegerField(default=0)
    protein = models.DecimalField(max_digits=6, decimal_places=1, default=0.0)
    carbs = models.DecimalField(max_digits=6, decimal_places=1, default=0.0)
    fat = models.DecimalField(max_digits=6, decimal_places=1, default=0.0)
    prep_time_minutes = models.PositiveIntegerField(default=0)
    MEAL_TYPE = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]

    meal_type = models.CharField(max_length=50, choices=MEAL_TYPE)
    ingredients = models.JSONField(default=list)
    preparation_steps = models.TextField(blank=True, null=True)
    is_recipe_of_the_day = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.title


class MealPlanPreference(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='meal_plan_preference')
    dietary_preferences = models.JSONField(default=list)
    allergies = models.JSONField(default=list)
    meal_types = models.JSONField(default=list)
    caloric_goal = models.PositiveBigIntegerField(blank=True, null=True)
    cooking_time_preference = models.CharField(max_length=50, blank=True, null=True)
    number_of_servings = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Meal Plan Preferences for {self.user.username}"


class GeneratedMealPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_meal_plans')
    date = models.DateField()
    recipes = models.ManyToManyField(Recipe, related_name='generated_meal_plans')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Generated Meal Plan for {self.user.username} at {self.created_at}"


class MealLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_logs')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    MEAL_TYPE = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]

    meal_type = models.CharField(max_length=50, choices=MEAL_TYPE)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=1)
    logged_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-logged_at']


    def __str__(self):
        return f"{self.meal_type} on {self.logged_at} for {self.user.username}"
 

class FavoriteRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_recipes')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)        
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')


    def __str__(self):
        return f"{self.user.username} favorited {self.recipe.title}"
