from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from meetings.models import Meeting, MeetingInsight


class MeetingTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='meetinguser', password='password123')
        self.client.login(username='meetinguser', password='password123')
        self.meeting = Meeting.objects.create(
            user=self.user,
            title='Sprint Kickoff',
            meeting_type='sprint',
            participants='Alice, Bob',
            transcript='Alice will deploy the build by Friday.'
        )

    def test_meeting_list_view(self):
        response = self.client.get(reverse('meeting_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sprint Kickoff')

    def test_meeting_search_filter(self):
        response = self.client.get(reverse('meeting_list') + '?q=Kickoff')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sprint Kickoff')

        response_empty = self.client.get(reverse('meeting_list') + '?q=Nonexistent')
        self.assertEqual(response_empty.status_code, 200)
        self.assertNotContains(response_empty, 'Sprint Kickoff')

    def test_meeting_create_view(self):
        response = self.client.post(reverse('meeting_create'), {
            'title': 'New Strategy Meeting',
            'date': '2026-08-17',
            'meeting_type': 'general',
            'participants': 'Charlie',
            'transcript': 'We discussed Q3 objectives.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Meeting.objects.filter(title='New Strategy Meeting').exists())

    def test_meeting_detail_view(self):
        response = self.client.get(reverse('meeting_detail', args=[self.meeting.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sprint Kickoff')
        self.assertContains(response, 'Alice will deploy')

    def test_meeting_delete_view(self):
        response = self.client.post(reverse('meeting_delete', args=[self.meeting.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Meeting.objects.filter(pk=self.meeting.pk).exists())
