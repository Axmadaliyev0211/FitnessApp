import html

from rest_framework import serializers
from .models import FAQ, SupportMessage


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ('id', 'question', 'answer', 'category', 'order')


class SupportMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportMessage
        fields = ('id', 'message', 'is_from_user', 'is_read', 'created_at')
        read_only_fields = ('id', 'is_from_user', 'created_at')


    def validate_message(self, value):
        return html.escape(value)


class SupportReplySerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    message = serializers.CharField()