import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from meetings.models import Meeting
from actions.models import ActionItem


class APITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='apiuser', password='password123')
        self.client.login(username='apiuser', password='password123')
        self.meeting = Meeting.objects.create(
            user=self.user,
            title='API Test Meeting',
            transcript='Elena will test the endpoints.'
        )

    def test_api_meeting_list(self):
        response = self.client.get(reverse('api_meeting_list_create'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue('results' in data or isinstance(data, list))

    def test_api_generate_insights(self):
        response = self.client.post(
            reverse('api_ai_generate'),
            data=json.dumps({'meeting_id': self.meeting.id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertIn('insights', data)
        self.assertIn('summary', data['insights'])

    def test_api_extract_action_items(self):
        action_data = [
            {
                'task': 'Deploy to production server',
                'owner': 'David',
                'due_date': '2026-08-25',
                'priority': 'HIGH'
            },
            {
                'task': 'Update customer changelog',
                'owner': '',
                'due_date': '',
                'priority': 'LOW'
            }
        ]
        response = self.client.post(
            reverse('api_ai_extract_actions'),
            data=json.dumps({
                'meeting_id': self.meeting.id,
                'action_items': action_data
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data.get('count'), 2)
        self.assertEqual(ActionItem.objects.filter(meeting=self.meeting).count(), 2)

    def test_api_dashboard_stats(self):
        response = self.client.get(reverse('api_dashboard_stats'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('total_meetings', data)
        self.assertIn('total_actions', data)
        self.assertIn('completion_rate', data)
