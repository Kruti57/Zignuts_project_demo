from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Meeting(models.Model):
    MEETING_TYPES = [
        ('sprint', 'Sprint Planning'),
        ('standup', 'Daily Standup'),
        ('client', 'Client Review'),
        ('one_on_one', '1-on-1 Sync'),
        ('retrospective', 'Retrospective'),
        ('board', 'Board / Executive'),
        ('general', 'General Meeting'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meetings')
    title = models.CharField(max_length=255)
    date = models.DateField(default=timezone.now)
    meeting_type = models.CharField(max_length=50, choices=MEETING_TYPES, default='sprint')
    participants = models.CharField(max_length=500, blank=True, help_text="Comma-separated participant names")
    transcript = models.TextField(blank=True, help_text="Full meeting transcript or notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.date})"

    @property
    def participants_list(self):
        if not self.participants:
            return []
        return [p.strip() for p in self.participants.split(',') if p.strip()]

    @property
    def has_insights(self):
        return hasattr(self, 'insights') and self.insights is not None

    @property
    def total_actions(self):
        return self.action_items.count()

    @property
    def completed_actions(self):
        return self.action_items.filter(status='COMPLETED').count()

    @property
    def open_actions(self):
        return self.action_items.filter(status__in=['OPEN', 'IN_PROGRESS', 'BLOCKED']).count()


class MeetingInsight(models.Model):
    meeting = models.OneToOneField(Meeting, on_delete=models.CASCADE, related_name='insights')
    summary = models.TextField(blank=True)
    discussion_points = models.JSONField(default=list, blank=True)
    key_decisions = models.JSONField(default=list, blank=True)
    risks_and_concerns = models.JSONField(default=list, blank=True)
    unanswered_questions = models.JSONField(default=list, blank=True)
    raw_ai_response = models.JSONField(default=dict, blank=True)
    ai_provider = models.CharField(max_length=50, default='mock')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"AI Insights for: {self.meeting.title}"
