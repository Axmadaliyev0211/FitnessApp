import html
from rest_framework import serializers
from .models import ProgressEntry, ActivityLog


class ProgressEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressEntry
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at')


    def validate_notes(self, value):
        if value:
            return html.escape(value)
        return value



class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at')
 