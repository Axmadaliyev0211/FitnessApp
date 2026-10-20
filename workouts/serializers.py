import html
from rest_framework import serializers
from .models import (WorkoutCategory, Exercise, 
                     Workout, WorkoutExercise, 
                     CustomRoutine, CustomRoutineExercise, 
                     UserWorkoutLog, ExerciseLog, FavoriteWorkout)


class WorkoutCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutCategory
        fields = '__all__'



class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = '__all__'




class WorkoutExerciseSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)
    exercise_id = serializers.UUIDField(write_only=True)

    class Meta: 
        model = WorkoutExercise
        fields = (
            'id', 'exercise', 'exercise_id', 'sets', 'reps',
            'duration_seconds', 'rest_seconds', 'order'
        )



class WorkoutSerializer(serializers.ModelSerializer):
    category = WorkoutCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=WorkoutCategory.objects.all(),
        source='category', write_only=True, required=False, allow_null=True
    )
    exercises = WorkoutExerciseSerializer(source='workout_exercises', many=True, read_only=True)

    class Meta:
        model = Workout
        fields = (
            'id', 'title', 'description', 'category', 'category_id',
            'difficulty_level', 'duration_minutes', 'calories_estimated',
            'image', 'is_premium', 'is_training_of_the_day',
            'exercises', 'created_at'
        )


# class WorkoutSerializer(serializers.ModelSerializer):
#     category = WorkoutCategorySerializer(read_only=True)
#     category_id = serializers.PrimaryKeyRelatedField(
#         queryset=WorkoutCategory.objects.all(),
#         source='category', write_only=True, required=False, allow_null=True
#     )
#     exercises = WorkoutExerciseSerializer(source='workout_exercises', many=True, read_only=True)

#     title = serializers.SerializerMethodField()
#     description = serializers.SerializerMethodField()

#     class Meta:
#         model = Workout
#         fields = (
#             'id', 'title', 'description', 'category', 'category_id',
#             'difficulty_level', 'duration_minutes', 'calories_estimated',
#             'image', 'is_premium', 'is_training_of_the_day',
#             'exercises', 'created_at'
#         )

#     def get_title(self, obj):
#         return {
#             'uz': obj.title_uz or '',
#             'en': obj.title_en or '',
#             'ru': obj.title_ru or '',
#         }

#     def get_description(self, obj):
#         return {
#             'uz': obj.description_uz or '',
#             'en': obj.description_en or '',
#             'ru': obj.description_ru or '',
#         }



class CustomRoutineExerciseSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)
    exercise_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = CustomRoutineExercise
        fields = (
            'id', 'exercise', 'exercise_id', 'sets', 'reps',
            'duration_seconds', 'rest_seconds', 'order', 'round_number'
        )



class CustomRoutineSerializer(serializers.ModelSerializer):
    exercises = CustomRoutineExerciseSerializer(source='custom_routine_exercises', many=True, read_only=True)

    class Meta:
        model = CustomRoutine
        fields = ('id', 'title', 'exercises', 'created_at')
        read_only_fields = ('id', 'created_at')


    def validate_title(self, value):
        return html.escape(value)


class ExerciseLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseLog
        fields = '__all__'
        read_only_fields = ('id',)



class UserWorkoutLogSerializer(serializers.ModelSerializer):
    exercise_logs = ExerciseLogSerializer(many=True, read_only=True)
    workout_title = serializers.CharField(source='workout.title', read_only=True)

    class Meta:
        model = UserWorkoutLog
        fields = (
            'id', 'user','workout', 'workout_title', 'custom_routine',
            'started_at', 'completed_at', 'duration_seconds',
            'calories_burned', 'rating', 'notes', 'exercise_logs', 'created_at'
        )
        read_only_fields = ('id', 'user', 'created_at')

    def validate_rating(self, value):
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("Rating 1 dan 5 gacha bo‘lishi kerak.")
        return value

    def validate_notes(self, value):
        if value:
            return html.escape(value)
        return value



class FavoriteWorkoutSerializer(serializers.ModelSerializer):
    workout_detail = WorkoutSerializer(source='workout', read_only=True)
    workout = serializers.PrimaryKeyRelatedField(queryset=Workout.objects.all())

    class Meta:
        model = FavoriteWorkout
        fields = ('id', 'workout', 'workout_detail', 'added_at')
        read_only_fields = ('id', 'added_at')


    def validate_workout(self, value):
        user = self.context['request'].user
        if FavoriteWorkout.objects.filter(user=user, workout=value).exists():
            raise serializers.ValidationError("Bu workout allaqachon sevimlilarda.")
        return value


        