from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import FAQViewSet, SupportMessageViewSet, SupportReplyView

router = DefaultRouter()
router.register('faqs', FAQViewSet, basename='faqs')
router.register('messages', SupportMessageViewSet, basename='support-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('reply/', SupportReplyView.as_view(), name='support-reply'),
]