from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    RegisterView, ProfileView, OnboardingView, DeleteAccountView,
    UserGoalViewSet, UserSettingsView, ForgotPasswordView, 
    ResetPasswordView, ChangePasswordView
)

router = DefaultRouter()
router.register('goals', UserGoalViewSet, basename='user-goals')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('me/', ProfileView.as_view(), name='profile'),
    path('onboarding/', OnboardingView.as_view(), name='onboarding'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete-account'),
    path('settings/', UserSettingsView.as_view(), name='settings'),
    path('', include(router.urls)),

    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]