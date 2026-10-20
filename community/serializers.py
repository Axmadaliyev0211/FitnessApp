import html
from rest_framework import serializers
from .models import (ForumCategory, ForumPost, 
                     ForumComment, Challenge, 
                     ChallengeRound, ChallengeExercise, 
                     UserChallenge, PostLike)

from workouts.serializers import ExerciseSerializer


class ForumCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ForumCategory
        fields = '__all__'
 

        

class ForumCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = ForumComment
        fields = ('id', 'post', 'user', 'user_name', 'content', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')


    def validate_content(self, value):
        return html.escape(value)




class ForumPostSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    comments = ForumCommentSerializer(many=True, read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = ForumPost
        fields = (
            'id',
            'category',
            'user',
            'user_name',
            'title',
            'content',
            'image',
            'likes_count',
            'comments_count',
            'is_liked',
            'comments',
            'created_at',
        )
        read_only_fields = (
            'id',
            'user',
            'likes_count',
            'comments_count',
            'is_liked',
            'created_at',
        )


    def validate_title(self, value):
        return html.escape(value)

    def validate_content(self, value):
        return html.escape(value)


    def get_is_liked(self, obj):
            request = self.context.get('request')
            if request and request.user.is_authenticated:
                return obj.likes.filter(user=request.user).exists()
            return False





class ChallengeExerciseSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)

    class Meta:
        model = ChallengeExercise
        fields = ('id', 'exercise', 'sets', 'reps', 'duration_seconds', 'order')




class ChallengeRoundSerializer(serializers.ModelSerializer):
    exercises = ChallengeExerciseSerializer(many=True, read_only=True)

    class Meta:
        model = ChallengeRound
        fields = ('id', 'title', 'order', 'exercises')




class ChallengeSerializer(serializers.ModelSerializer):
    rounds = ChallengeRoundSerializer(many=True, read_only=True)

    class Meta:
        model = Challenge
        fields = (
            'id', 'title', 'description', 'image', 'difficulty_level',
            'is_weekly', 'start_date', 'end_date', 'rounds', 'created_at'
        )




class UserChallengeSerializer(serializers.ModelSerializer):
    challenge = serializers.PrimaryKeyRelatedField(queryset=Challenge.objects.filter(is_active=True))
    challenge_detail = ChallengeSerializer(source='challenge', read_only=True)

    class Meta:
        model = UserChallenge
        fields = (
            'id', 'challenge', 'challenge_detail', 'status',
            'start_date', 'end_date', 'total_calories', 'total_duration'
        )
        read_only_fields = (
            'id', 'status', 'start_date', 'end_date',
            'total_calories', 'total_duration'
        )


    def validate_challenge(self, value):
        user = self.context['request'].user
        if UserChallenge.objects.filter(user=user, challenge=value).exists():
            raise serializers.ValidationError("Siz bu challenge ga allaqachon qo‘shilgansiz.")
        return value


class PostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLike
        fields = ('id', 'post', 'created_at')
        read_only_fields = ('id', 'created_at')