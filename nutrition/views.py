from django.db import models
from django.shortcuts import render
from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.response import Response
import django_filters.rest_framework
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.exceptions import ValidationError
from datetime import datetime

from .models import Recipe, MealPlanPreference, GeneratedMealPlan, MealLog, FavoriteRecipe
from .serializers import (
    RecipeSerializer, MealPlanPreferenceSerializer,
    GeneratedMealPlanSerializer, MealLogSerializer, FavoriteRecipeSerializer
)
from core.permissions import IsOwner
from core.language import set_language_from_user


class RecipeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Recipe.objects.filter(is_active=True)
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['meal_type']
    search_fields = ['title']

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        set_language_from_user(request)

    @action(detail=False, methods=['get'])
    def recipe_of_the_day(self, request):
        recipe = Recipe.objects.filter(is_recipe_of_the_day=True, is_active=True).first()
        if not recipe:
            return Response({"detail": "Bugungi retsept topilmadi."}, status=404)
        serializer = self.get_serializer(recipe)
        return Response(serializer.data)


    @action(detail=False, methods=['get'])
    def recommended(self, request):
        qs = self.get_queryset().filter(is_active=True).order_by('-created_at')[:10]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class MealPlanPreferenceView(generics.RetrieveUpdateAPIView):
    serializer_class = MealPlanPreferenceSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head', 'options']

    def get_object(self):
        obj, _ = MealPlanPreference.objects.get_or_create(user=self.request.user)
        return obj

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class GeneratedMealPlanViewSet(viewsets.ModelViewSet):
    serializer_class = GeneratedMealPlanSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        return GeneratedMealPlan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        preference = getattr(user, 'meal_plan_preference', None)

        recipes = Recipe.objects.filter(is_active=True)

        if preference:
            # 1. Kaloriya limiti
            if preference.caloric_goal:
                recipes = recipes.filter(calories__lte=preference.caloric_goal)

            # 2. Meal type (breakfast, lunch, dinner, snack)
            if preference.meal_types:
                recipes = recipes.filter(meal_type__in=preference.meal_types)

            # 3. Cooking time
            if preference.cooking_time_preference:
                # Masalan: "less_15", "15_30", "more_30"
                if preference.cooking_time_preference == 'less_15':
                    recipes = recipes.filter(prep_time_minutes__lte=15)
                elif preference.cooking_time_preference == '15_30':
                    recipes = recipes.filter(prep_time_minutes__gt=15, prep_time_minutes__lte=30)
                elif preference.cooking_time_preference == 'more_30':
                    recipes = recipes.filter(prep_time_minutes__gt=30)

            # 4. Dietary preferences (vegan, keto, vegetarian...)
            # ingredients yoki description da qidirish (sodda variant)
            if preference.dietary_preferences:
                for diet in preference.dietary_preferences:
                    recipes = recipes.filter(
                        models.Q(title__icontains=diet) |
                        models.Q(description__icontains=diet) |
                        models.Q(ingredients__icontains=diet)
                    )

            # 5. Allergies — allergy so‘zi ingredients da bo‘lmasin
            if preference.allergies:
                for allergy in preference.allergies:
                    recipes = recipes.exclude(ingredients__icontains=allergy)

        # Porsiya soniga qarab nechta retsept olish
        limit = 5
        if preference and preference.number_of_servings:
            limit = min(preference.number_of_servings * 2, 10)  # taxminiy

        selected_recipes = list(recipes.order_by('?')[:limit])  # tasodifiy tanlash

        meal_plan = serializer.save(user=user)
        meal_plan.recipes.set(selected_recipes)


class MealLogViewSet(viewsets.ModelViewSet):
    serializer_class = MealLogSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return MealLog.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        date_str = request.query_params.get('date')
        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError({"date": "Format noto‘g‘ri. YYYY-MM-DD ishlating."})
        else:
            date = datetime.today().date()

        logs = self.get_queryset().filter(logged_at__date=date)

        total_calories = total_protein = total_carbs = total_fat = 0
        meals = {'breakfast': 0, 'lunch': 0, 'dinner': 0, 'snack': 0}

        for log in logs:
            qty = float(log.quantity)
            total_calories += log.recipe.calories * qty
            total_protein += float(log.recipe.protein) * qty
            total_carbs += float(log.recipe.carbs) * qty
            total_fat += float(log.recipe.fat) * qty
            meals[log.meal_type] += log.recipe.calories * qty

        return Response({
            "date": date,
            "total_calories": round(total_calories, 1),
            "protein": round(total_protein, 1),
            "carbs": round(total_carbs, 1),
            "fat": round(total_fat, 1),
            "meals": meals
        })


class FavoriteRecipeViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteRecipeSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        return FavoriteRecipe.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

