from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RecipeViewSet, MealPlanPreferenceView, GeneratedMealPlanViewSet,
    MealLogViewSet, FavoriteRecipeViewSet
)

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('meal-plans', GeneratedMealPlanViewSet, basename='meal-plans')
router.register('meal-logs', MealLogViewSet, basename='meal-logs')
router.register('favorites', FavoriteRecipeViewSet, basename='favorite-recipes')

urlpatterns = [
    path('preferences/', MealPlanPreferenceView.as_view(), name='meal-preferences'),
    path('', include(router.urls)),
]