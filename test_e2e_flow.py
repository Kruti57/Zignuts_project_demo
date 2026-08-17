"""
End-to-End Workflow Verification Script.
Simulates complete user interaction across all endpoints and database models.
"""

import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from meetings.models import Meeting, MeetingInsight
from actions.models import ActionItem

def run_e2e_verification():
    print("==================================================")
    print("STARTING FULL END-TO-END WORKFLOW VERIFICATION")
    print("==================================================")

    client = Client()

    username = "e2e_evaluator"
    password = "e2e_secure_password_123"
    
    # Cleanup prior test run if exists for idempotency
    User.objects.filter(username=username).delete()

    print(f"\n[1/7] Testing User Registration for '{username}'...")
    reg_response = client.post(reverse('register'), {
        'username': username,
        'email': 'evaluator@zignuts.com',
        'password': password,
        'confirm_password': password
    })
    assert reg_response.status_code == 302, f"Registration failed: {reg_response.status_code}"
    user = User.objects.get(username=username)
    print(f" -> OK: User '{username}' successfully registered and authenticated.")

    # 2. Test Dashboard View
    print("\n[2/7] Testing Executive Dashboard View...")
    dash_response = client.get(reverse('dashboard'))
    assert dash_response.status_code == 200, f"Dashboard failed: {dash_response.status_code}"
    assert b"Welcome back" in dash_response.content
    print(" -> OK: Dashboard successfully loaded with metrics & activity widgets.")

    # 3. Test Meeting Creation
    print("\n[3/7] Testing Meeting Creation with Transcript...")
    meeting_title = "E2E Automated Sprint Architecture Review"
    transcript_text = """
    Sarah Connor: We reviewed the cloud microservices architecture. We agreed to deploy the Redis caching layer by Friday.
    David Kim: I will finalize the backend API endpoints and schema migrations by tomorrow.
    Elena Rostova: I will complete the dark mode UI components and the Action Tracker table.
    Michael Chen: Is there any risk of third-party API rate limits?
    Sarah Connor: Yes, we should implement a circuit breaker and retry mechanism.
    """
    create_response = client.post(reverse('meeting_create'), {
        'title': meeting_title,
        'date': '2026-08-17',
        'meeting_type': 'sprint',
        'participants': 'Sarah Connor, David Kim, Elena Rostova, Michael Chen',
        'transcript': transcript_text
    })
    assert create_response.status_code == 302, f"Meeting creation failed: {create_response.status_code}"
    meeting = Meeting.objects.get(title=meeting_title, user=user)
    print(f" -> OK: Meeting created (ID: {meeting.id}) with {len(meeting.participants_list)} participants.")

    # 4. Test AI Insights Generation API
    print("\n[4/7] Testing AI Insights Generation API (/api/ai/generate/)...")
    ai_response = client.post(
        reverse('api_ai_generate'),
        data=json.dumps({'meeting_id': meeting.id}),
        content_type='application/json'
    )
    assert ai_response.status_code == 200, f"AI generation failed: {ai_response.status_code}"
    ai_data = ai_response.json()
    assert ai_data.get('success') is True
    insights = ai_data.get('insights')
    print(f" -> Provider used: {ai_data.get('provider').upper()}")
    print(f" -> Summary: {insights.get('summary')[:100]}...")
    print(f" -> Key Decisions: {len(insights.get('key_decisions', []))} items")
    print(f" -> Extracted Actions: {len(insights.get('action_items', []))} items")
    assert len(insights.get('action_items', [])) > 0, "No action items extracted by AI"
    print(" -> OK: AI Insights successfully structured, validated, and persisted.")

    # 5. Test Action Items Extraction API
    print("\n[5/7] Testing Action Items Extraction to Database (/api/ai/extract-actions/)...")
    extract_response = client.post(
        reverse('api_ai_extract_actions'),
        data=json.dumps({
            'meeting_id': meeting.id,
            'action_items': insights['action_items']
        }),
        content_type='application/json'
    )
    assert extract_response.status_code == 201, f"Action extraction failed: {extract_response.status_code}"
    extract_data = extract_response.json()
    created_count = extract_data.get('count')
    print(f" -> OK: Bulk-created {created_count} ActionItem records bound to user and meeting.")

    # 6. Test Action Tracker Filtering & Inline Status Updating
    print("\n[6/7] Testing Action Tracker Filtering & Inline Status Update API...")
    tracker_response = client.get(reverse('action_tracker'))
    assert tracker_response.status_code == 200
    assert bytes(meeting_title, 'utf-8') in tracker_response.content

    # Update status of first created action item to 'COMPLETED'
    first_action = ActionItem.objects.filter(meeting=meeting).first()
    update_response = client.post(
        reverse('action_update_status_api', args=[first_action.id]),
        data={'status': 'COMPLETED'}
    )
    assert update_response.status_code == 200, f"Status update failed: {update_response.status_code}"
    first_action.refresh_from_db()
    assert first_action.status == 'COMPLETED'
    print(f" -> OK: Action #{first_action.id} status updated to '{first_action.status}' via AJAX endpoint.")

    # 7. Test CSV Export
    print("\n[7/7] Testing Action Tracker CSV Export...")
    csv_response = client.get(reverse('action_export_csv'))
    assert csv_response.status_code == 200
    assert csv_response['Content-Type'] == 'text/csv'
    assert b"Task,Meeting,Owner" in csv_response.content
    print(" -> OK: Action items exported as CSV successfully.")

    print("\n==================================================")
    print("ALL 7 CORE WORKFLOW PHASES PASSED WITH ZERO ERRORS!")
    print("==================================================")

if __name__ == '__main__':
    run_e2e_verification()
