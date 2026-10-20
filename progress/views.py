from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timedelta
from django.utils import timezone

from .models import ProgressEntry, ActivityLog
from .serializers import ProgressEntrySerializer, ActivityLogSerializer
from core.permissions import IsOwner
from core.language import set_language_from_user


class ProgressEntryViewSet(viewsets.ModelViewSet):
    serializer_class = ProgressEntrySerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['date']

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        set_language_from_user(request)

    def get_queryset(self):
        return ProgressEntry.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def charts(self, request):
        period = request.query_params.get('period', 'month')
        today = timezone.now().date()

        if period == 'week':
            start_date = today - timedelta(days=7)
        elif period == 'year':
            start_date = today - timedelta(days=365)
        else:
            start_date = today - timedelta(days=30)

        entries = ProgressEntry.objects.filter(user=request.user, date__gte=start_date).order_by('date')
        activity = ActivityLog.objects.filter(user=request.user, date__gte=start_date).order_by('date')

        return Response({
            "period": period,
            "weight": [{"date": e.date, "weight": e.weight_kg} for e in entries if e.weight_kg],
            "steps": [{"date": a.date, "steps": a.steps, "calories": a.calories_burned} for a in activity]
        })


class ActivityLogViewSet(viewsets.ModelViewSet):
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['date']

    def get_queryset(self):
        return ActivityLog.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

