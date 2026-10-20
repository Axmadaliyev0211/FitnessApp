from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.dateparse import parse_datetime
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import (
    WorkoutCategory, Exercise, Workout, CustomRoutine,
    UserWorkoutLog, FavoriteWorkout
)
from .serializers import (
    WorkoutCategorySerializer, ExerciseSerializer, WorkoutSerializer,
    CustomRoutineSerializer, UserWorkoutLogSerializer, FavoriteWorkoutSerializer
)
from core.permissions import IsOwner, IsTrainerOrAdmin
from core.language import set_language_from_user


class WorkoutCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WorkoutCategory.objects.all()
    serializer_class = WorkoutCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        set_language_from_user(request)


class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Exercise.objects.filter(is_active=True)
    serializer_class = ExerciseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['difficulty_level']

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        set_language_from_user(request)


class WorkoutViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['difficulty_level', 'category', 'is_premium', 'is_training_of_the_day']
    search_fields = ['title']
    ordering_fields = ['created_at', 'duration_minutes']

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        set_language_from_user(request)

    def get_queryset(self):
        qs = Workout.objects.filter(is_active=True)
        user = self.request.user
        if user.is_authenticated and not user.is_premium and not user.is_staff:
            qs = qs.filter(is_premium=False)
        return qs

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsTrainerOrAdmin()]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def training_of_the_day(self, request):
        workout = self.get_queryset().filter(is_training_of_the_day=True).first()
        if not workout:
            return Response({"detail": "Bugun Training of the Day yo‘q"}, status=404)
        return Response(self.get_serializer(workout).data)

    @action(detail=False, methods=['get'])
    def recommended(self, request):
        user = request.user
        qs = self.get_queryset()

        if user.is_authenticated and getattr(user, 'fitness_level', None):
            qs = qs.filter(difficulty_level=user.fitness_level)

        if user.is_authenticated and not user.is_premium:
            qs = qs.filter(is_premium=False)

        qs = qs.order_by('-created_at')[:10]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class CustomRoutineViewSet(viewsets.ModelViewSet):
    serializer_class = CustomRoutineSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return CustomRoutine.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserWorkoutLogViewSet(viewsets.ModelViewSet):
    serializer_class = UserWorkoutLogSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return UserWorkoutLog.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        log = self.get_object()

        completed_at = request.data.get('completed_at')
        if completed_at:
            parsed = parse_datetime(completed_at)
            if parsed is None:
                raise ValidationError({"completed_at": "Noto‘g‘ri sana formati."})
            log.completed_at = parsed

        duration = request.data.get('duration_seconds')
        if duration is not None:
            try:
                log.duration_seconds = int(duration)
            except (TypeError, ValueError):
                raise ValidationError({"duration_seconds": "Butun son bo‘lishi kerak."})

        rating = request.data.get('rating')
        if rating is not None:
            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    raise ValidationError({"rating": "1 dan 5 gacha bo‘lishi kerak."})
                log.rating = rating
            except (TypeError, ValueError):
                raise ValidationError({"rating": "1 dan 5 gacha butun son."})

        if 'notes' in request.data:
            log.notes = request.data.get('notes')

        log.calories_burned = request.data.get('calories_burned', log.calories_burned)
        log.save()

        return Response(self.get_serializer(log).data)


class FavoriteWorkoutViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteWorkoutSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        return FavoriteWorkout.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

