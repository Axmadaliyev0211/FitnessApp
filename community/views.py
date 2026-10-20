from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.utils.dateparse import parse_datetime
from rest_framework.exceptions import ValidationError
from notifications.utils import create_notification

from .models import ForumCategory, ForumPost, ForumComment, Challenge, UserChallenge, PostLike
from .serializers import (
    ForumCategorySerializer, ForumPostSerializer, ForumCommentSerializer,
    ChallengeSerializer, UserChallengeSerializer, PostLikeSerializer
)
from core.permissions import IsOwner, IsOwnerOrReadOnly
from core.language import set_language_from_user


class ForumCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ForumCategory.objects.all()
    serializer_class = ForumCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        set_language_from_user(request)


class ForumPostViewSet(viewsets.ModelViewSet):
    serializer_class = ForumPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['category']
    search_fields = ['title', 'content']

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        set_language_from_user(request)

    def get_queryset(self):
        return ForumPost.objects.select_related('user', 'category').prefetch_related('comments', 'likes')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ForumCommentViewSet(viewsets.ModelViewSet):
    serializer_class = ForumCommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['post']

    def get_queryset(self):
        qs = ForumComment.objects.select_related('user', 'post')
        post_id = self.request.query_params.get('post')
        if post_id:
            qs = qs.filter(post_id=post_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ChallengeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Challenge.objects.filter(is_active=True)
    serializer_class = ChallengeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        set_language_from_user(request)

    @action(detail=False, methods=['get'])
    def weekly(self, request):
        challenge = self.get_queryset().filter(is_weekly=True).first()
        if not challenge:
            return Response({"detail": "Hozircha Weekly Challenge yo'q"}, status=404)
        return Response(self.get_serializer(challenge).data)


class UserChallengeViewSet(viewsets.ModelViewSet):
    serializer_class = UserChallengeSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    http_method_names = ['get', 'post', 'patch']

    def get_queryset(self):
        return UserChallenge.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        obj = self.get_object()
        obj.status = 'completed'

        end_date = request.data.get('end_date')
        if end_date:
            parsed = parse_datetime(end_date)
            if parsed is None:
                raise ValidationError({"end_date": "Noto‘g‘ri sana formati."})
            obj.end_date = parsed

        obj.total_calories = request.data.get('total_calories', obj.total_calories)
        obj.total_duration = request.data.get('total_duration', obj.total_duration)
        obj.save()

        create_notification(
            user=request.user,
            title="Challenge yakunlandi!",
            body=f"Tabriklaymiz, siz '{obj.challenge.title}' challengeni tugatdingiz.",
            type='challenge'
        )

        return Response(self.get_serializer(obj).data)


class PostLikeViewSet(viewsets.ModelViewSet):
    serializer_class = PostLikeSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        return PostLike.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        post_id = request.data.get('post')
        if not post_id:
            return Response({"detail": "post maydoni majburiy"}, status=400)

        if not ForumPost.objects.filter(id=post_id).exists():
            return Response({"detail": "Post topilmadi"}, status=404)

        like, created = PostLike.objects.get_or_create(user=request.user, post_id=post_id)
        if not created:
            like.delete()
            return Response({"liked": False}, status=200)

        return Response({"liked": True}, status=201)

