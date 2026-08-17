from datetime import timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from meetings.models import Meeting
from actions.models import ActionItem


class ActionItemTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='actionuser', password='password123')
        self.client.login(username='actionuser', password='password123')
        self.meeting = Meeting.objects.create(
            user=self.user,
            title='Demo Sync',
            meeting_type='standup'
        )
        self.today = timezone.localdate()
        self.action = ActionItem.objects.create(
            user=self.user,
            meeting=self.meeting,
            task='Fix CSS navbar bug',
            owner='Sarah',
            due_date=self.today + timedelta(days=2),
            priority='HIGH',
            status='OPEN'
        )

    def test_action_tracker_view(self):
        response = self.client.get(reverse('action_tracker'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fix CSS navbar bug')
        self.assertContains(response, 'Sarah')

    def test_action_overdue_property(self):
        overdue_action = ActionItem.objects.create(
            user=self.user,
            task='Overdue task',
            owner='Dave',
            due_date=self.today - timedelta(days=2),
            priority='MEDIUM',
            status='OPEN'
        )
        self.assertTrue(overdue_action.is_overdue)

        # Once completed, it shouldn't be considered overdue
        overdue_action.status = 'COMPLETED'
        overdue_action.save()
        self.assertFalse(overdue_action.is_overdue)

    def test_action_update_status_api(self):
        response = self.client.post(reverse('action_update_status_api', args=[self.action.pk]), {
            'status': 'COMPLETED'
        })
        self.assertEqual(response.status_code, 200)
        self.action.refresh_from_db()
        self.assertEqual(self.action.status, 'COMPLETED')

    def test_action_export_csv(self):
        response = self.client.get(reverse('action_export_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertContains(response, 'Fix CSS navbar bug')
