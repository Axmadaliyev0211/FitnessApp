import html
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, UserGoal, UserSettings



class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'nickname',      # foydalanuvchi shuni kiritadi
            'full_name',
            'password',
            'password2',
            'phone_number'
        )

        extra_kwargs = {
            'phone_number': {'required': False},
            'nickname': {'required': True},
        }

    def validate_nickname(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Bu nickname band.")
        if User.objects.filter(nickname__iexact=value).exists():
            raise serializers.ValidationError("Bu nickname band.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Parollar mos kelmadi"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        validated_data['username'] = validated_data['nickname']
        user = User.objects.create_user(**validated_data)
        UserSettings.objects.create(user=user)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'full_name', 'nickname', 'phone_number', 'avatar',
            'gender', 'date_of_birth', 'height_cm', 'weight_kg',
            'fitness_level', 'primary_goal', 'is_premium', 'is_trainer',
            'fingerprint_enabled', 'date_joined'
        )
        read_only_fields = ('id', 'email', 'is_premium', 'is_trainer', 'date_joined')


    def update(self, instance, validated_data):
        nickname = validated_data.get('nickname')
        if nickname and nickname != instance.nickname:
            if User.objects.filter(username__iexact=nickname).exclude(pk=instance.pk).exists():
                raise serializers.ValidationError({"nickname": "Bu nickname band."})
            validated_data['username'] = nickname  # username ham yangilanadi
        return super().update(instance, validated_data)


class UserGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGoal
        fields = (
            'id', 'goal_type', 'title', 'target_value', 'current_value',
            'unit', 'start_date', 'end_date', 'status', 'created_at'
        )
        read_only_fields = ('id', 'created_at')

    def validate(self, attrs):
        start = attrs.get('start_date') or getattr(self.instance, 'start_date', None)
        end = attrs.get('end_date') or getattr(self.instance, 'end_date', None)
        if start and end and end < start:
            raise serializers.ValidationError({"end_date": "Tugash sanasi boshlanishidan oldin bo‘lishi mumkin emas."})
        return attrs

    def validate_title(self, value):
        return html.escape(value)


class UserSettingsSerializer(serializers.ModelSerializer):
    language = serializers.ChoiceField(
        choices=[('uz', 'O\'zbekcha'), ('en', 'English'), ('ru', 'Русский')],
        required=False
    )

    class Meta:
        model = UserSettings
        fields = (
            'notifications_enabled', 'sound_enabled', 'do_not_disturb_enabled',
            'vibrate_enabled', 'lock_screen_enabled', 'reminder_enabled',
            'language'
        )



class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Bu email bilan foydalanuvchi topilmadi.")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Parollar mos kelmadi"})
        return attrs



class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Joriy parol noto'g'ri.")
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Parollar mos kelmadi"})
        return attrs


class OnboardingSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'gender', 'date_of_birth', 'height_cm', 'weight_kg',
            'fitness_level', 'primary_goal'
        )

        