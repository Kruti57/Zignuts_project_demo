from rest_framework import serializers
from django.contrib.auth.models import User
from meetings.models import Meeting, MeetingInsight
from actions.models import ActionItem


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class ActionItemSerializer(serializers.ModelSerializer):
    meeting_title = serializers.CharField(source='meeting.title', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    priority_badge_class = serializers.CharField(read_only=True)
    status_badge_class = serializers.CharField(read_only=True)

    class Meta:
        model = ActionItem
        fields = [
            'id', 'user', 'meeting', 'meeting_title', 'task', 'owner',
            'due_date', 'priority', 'status', 'is_overdue',
            'priority_badge_class', 'status_badge_class',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class MeetingInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingInsight
        fields = [
            'id', 'meeting', 'summary', 'discussion_points',
            'key_decisions', 'risks_and_concerns', 'unanswered_questions',
            'raw_ai_response', 'ai_provider', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MeetingSerializer(serializers.ModelSerializer):
    participants_list = serializers.ListField(read_only=True)
    has_insights = serializers.BooleanField(read_only=True)
    total_actions = serializers.IntegerField(read_only=True)
    completed_actions = serializers.IntegerField(read_only=True)
    open_actions = serializers.IntegerField(read_only=True)

    class Meta:
        model = Meeting
        fields = [
            'id', 'user', 'title', 'date', 'meeting_type', 'participants',
            'participants_list', 'transcript', 'has_insights',
            'total_actions', 'completed_actions', 'open_actions',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class MeetingDetailSerializer(MeetingSerializer):
    insights = MeetingInsightSerializer(read_only=True)
    action_items = ActionItemSerializer(many=True, read_only=True)

    class Meta(MeetingSerializer.Meta):
        fields = MeetingSerializer.Meta.fields + ['insights', 'action_items']
