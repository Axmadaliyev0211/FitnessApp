from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    WorkoutCategoryViewSet, ExerciseViewSet, WorkoutViewSet,
    CustomRoutineViewSet, UserWorkoutLogViewSet, FavoriteWorkoutViewSet
)

router = DefaultRouter()
router.register('categories', WorkoutCategoryViewSet, basename='workout-categories')
router.register('exercises', ExerciseViewSet, basename='exercises')
router.register('workouts', WorkoutViewSet, basename='workouts')
router.register('custom-routines', CustomRoutineViewSet, basename='custom-routines')
router.register('logs', UserWorkoutLogViewSet, basename='workout-logs')
router.register('favorites', FavoriteWorkoutViewSet, basename='favorite-workouts')

urlpatterns = [
    path('', include(router.urls)),
]