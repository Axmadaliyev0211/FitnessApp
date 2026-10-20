from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from workouts.models import Workout, Exercise
from nutrition.models import Recipe
from content.models import Article
from workouts.serializers import WorkoutSerializer, ExerciseSerializer
from nutrition.serializers import RecipeSerializer
from content.serializers import ArticleSerializer
from core.language import set_language_from_user


class GlobalSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        set_language_from_user(request)

        q = request.query_params.get('q', '').strip()
        search_type = request.query_params.get('type', 'all')
        results = {}

        if not q:
            return Response(results)

        if search_type in ['all', 'workout']:
            workouts = Workout.objects.filter(
                title__icontains=q,
                is_active=True
            )
            if request.user.is_authenticated and not request.user.is_premium:
                workouts = workouts.filter(is_premium=False)
            results["workouts"] = WorkoutSerializer(
                workouts[:10], many=True, context={'request': request}
            ).data

        if search_type in ['all', 'nutrition']:
            recipes = Recipe.objects.filter(
                title__icontains=q,
                is_active=True
            )[:10]
            results["recipes"] = RecipeSerializer(
                recipes, many=True, context={'request': request}
            ).data

        if search_type in ['all', 'article']:
            articles = Article.objects.filter(
                title__icontains=q,
                published_at__isnull=False
            )[:10]
            results["articles"] = ArticleSerializer(
                articles, many=True, context={'request': request}
            ).data

        return Response(results)