from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ForumCategoryViewSet, ForumPostViewSet, ForumCommentViewSet,
    ChallengeViewSet, UserChallengeViewSet, PostLikeViewSet
)

router = DefaultRouter()
router.register('categories', ForumCategoryViewSet, basename='forum-categories')
router.register('posts', ForumPostViewSet, basename='forum-posts')
router.register('comments', ForumCommentViewSet, basename='forum-comments')
router.register('challenges', ChallengeViewSet, basename='challenges')
router.register('my-challenges', UserChallengeViewSet, basename='user-challenges')
router.register('likes', PostLikeViewSet, basename='post-likes')

urlpatterns = [
    path('', include(router.urls)),
]