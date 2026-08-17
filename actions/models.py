from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ActionItem(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]

    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('BLOCKED', 'Blocked'),
        ('COMPLETED', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='action_items')
    meeting = models.ForeignKey(
        'meetings.Meeting',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='action_items'
    )
    task = models.TextField()
    owner = models.CharField(max_length=150, default='Unassigned')
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.task[:40]} - {self.owner} ({self.status})"

    @property
    def is_overdue(self):
        if self.due_date and self.status != 'COMPLETED':
            return self.due_date < timezone.localdate()
        return False

    @property
    def priority_badge_class(self):
        mapping = {
            'HIGH': 'bg-danger-subtle text-danger border-danger-subtle',
            'MEDIUM': 'bg-warning-subtle text-warning-emphasis border-warning-subtle',
            'LOW': 'bg-info-subtle text-info-emphasis border-info-subtle',
        }
        return mapping.get(self.priority, 'bg-secondary-subtle text-secondary')

    @property
    def status_badge_class(self):
        mapping = {
            'OPEN': 'bg-primary-subtle text-primary border-primary-subtle',
            'IN_PROGRESS': 'bg-info-subtle text-info-emphasis border-info-subtle',
            'BLOCKED': 'bg-danger-subtle text-danger border-danger-subtle',
            'COMPLETED': 'bg-success-subtle text-success border-success-subtle',
        }
        return mapping.get(self.status, 'bg-secondary-subtle text-secondary')
