from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProgressEntryViewSet, ActivityLogViewSet

router = DefaultRouter()
router.register('entries', ProgressEntryViewSet, basename='progress-entries')
router.register('activity', ActivityLogViewSet, basename='activity-logs')

urlpatterns = [
    path('', include(router.urls)),
]
