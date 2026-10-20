from django.shortcuts import render
from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings

from notifications.utils import create_notification

from .models import UserGoal, UserSettings
from .serializers import (
    UserRegisterSerializer, UserSerializer,
    UserGoalSerializer, UserSettingsSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer,
    ChangePasswordSerializer, OnboardingSerializer
)
from core.permissions import IsOwner
from core.language import set_language_from_user

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user




class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Barcha JWT tokenlarni blacklist qilish
        tokens = OutstandingToken.objects.filter(user=user)
        for token in tokens:
            BlacklistedToken.objects.get_or_create(token=token)

        user.is_active = False
        user.save()

        return Response(
            {"detail": "Hisob o‘chirildi."},
            status=status.HTTP_200_OK
        )


class UserGoalViewSet(viewsets.ModelViewSet):
    serializer_class = UserGoalSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        set_language_from_user(request)

    def get_queryset(self):
        return UserGoal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        goal = self.get_object()
        goal.status = 'completed'
        goal.save()

        create_notification(
            user=request.user,
            title="Maqsad bajarildi!",
            body=f"Siz '{goal.title}' maqsadingizni muvaffaqiyatli bajardingiz.",
            type='goal'
        )

        return Response(self.get_serializer(goal).data)
 

class UserSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        settings, _ = UserSettings.objects.get_or_create(user=self.request.user)
        return settings



class ForgotPasswordView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.get(email__iexact=email)

        token = PasswordResetTokenGenerator().make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        reset_link = f"{frontend_url}/reset-password/?uid={uid}&token={token}"

        # Email yuborish
        send_mail(
            subject="Parolni tiklash",
            message=f"Parolni tiklash uchun link:\n{reset_link}\n\nAgar bu so‘rovni siz yubormagan bo‘lsangiz, e'tibor bermang.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response(
            {"detail": "Parolni tiklash linki emailingizga yuborildi."},
            status=status.HTTP_200_OK
        )


class ResetPasswordView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            uid = force_str(urlsafe_base64_decode(serializer.validated_data['uid']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"detail": "Noto‘g‘ri link."}, status=status.HTTP_400_BAD_REQUEST)

        token = serializer.validated_data['token']
        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({"detail": "Token yaroqsiz yoki muddati o‘tgan."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({"detail": "Parol muvaffaqiyatli o‘zgartirildi."}, status=status.HTTP_200_OK)



class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({"detail": "Parol muvaffaqiyatli o‘zgartirildi."})


class OnboardingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OnboardingSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)