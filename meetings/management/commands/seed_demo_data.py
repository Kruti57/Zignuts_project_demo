from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from meetings.models import Meeting, MeetingInsight
from actions.models import ActionItem
from ai_service.mock_ai import generate_mock_insights


class Command(BaseCommand):
    help = "Seeds initial demo user, meetings, transcripts, AI insights, and action items"

    def handle(self, *args, **options):
        # 1. Create or get Demo User
        username = "demo"
        email = "demo@syncmind.ai"
        password = "demo_password_2026"

        user, created = User.objects.get_or_create(username=username, defaults={'email': email})
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created demo user: '{username}' (password: '{password}')"))
        else:
            self.stdout.write(self.style.WARNING(f"Demo user '{username}' already exists."))

        today = timezone.localdate()

        # 2. Meeting 1: Zignuts Assessment Primary Demo Meeting
        m1, _ = Meeting.objects.get_or_create(
            user=user,
            title="Zignuts AI Platform Architecture & Sprint Deliverables Review",
            defaults={
                'date': today - timedelta(days=2),
                'meeting_type': 'sprint',
                'participants': 'Sarah Connor (Tech Lead), David Kim (Backend Lead), Elena Rostova (Frontend Lead), Michael Chen (Product Manager)',
                'transcript': """Sarah Connor (Tech Lead): Welcome everyone. Our main goal for this sprint is closing the customer onboarding bottleneck and finalizing the AI Meeting Notes integration.
David Kim (Backend): On the backend architecture, Sarah and I reviewed the schema. We decided to use MySQL with PyMySQL connection pooling for high throughput. I will finalize the database migration scripts and set up the DRF endpoints by Friday.
Elena Rostova (Frontend): On the frontend, I am building the modern SaaS dashboard and the Action Tracker. I will complete the Quill rich text editor and the dark mode theme by Thursday.
Michael Chen (Product): Great. Sarah, what about the AI service fallback?
Sarah Connor: We agreed that if the Gemini API key is missing or rate limited, the system must seamlessly fall back to an intelligent structured mock AI without throwing errors. I will write the AI client wrapper and validation tests by tomorrow.
David Kim: One concern: what if the external webhook experiences latency during action item sync?
Sarah Connor: That is a potential risk. We should add retry logic and timeout limits.
Elena Rostova: Michael, do we need multi-language transcript support in this phase?
Michael Chen: That is an open question. Let's verify customer demand before scoping it for next quarter."""
            }
        )

        insights_1 = generate_mock_insights(m1.title, m1.transcript, m1.participants, m1.get_meeting_type_display())
        MeetingInsight.objects.update_or_create(
            meeting=m1,
            defaults={
                'summary': insights_1['summary'],
                'discussion_points': insights_1['discussion_points'],
                'key_decisions': insights_1['key_decisions'],
                'risks_and_concerns': insights_1['risks_and_concerns'],
                'unanswered_questions': insights_1['unanswered_questions'],
                'raw_ai_response': insights_1,
                'ai_provider': 'mock'
            }
        )

        # Action Items for Meeting 1
        ActionItem.objects.get_or_create(
            user=user,
            meeting=m1,
            task="Finalize database migrations and DRF endpoints",
            defaults={
                'owner': 'David Kim',
                'due_date': today + timedelta(days=3),
                'priority': 'HIGH',
                'status': 'IN_PROGRESS'
            }
        )

        ActionItem.objects.get_or_create(
            user=user,
            meeting=m1,
            task="Build modern SaaS dashboard and action tracker UI",
            defaults={
                'owner': 'Elena Rostova',
                'due_date': today + timedelta(days=2),
                'priority': 'HIGH',
                'status': 'COMPLETED'
            }
        )

        ActionItem.objects.get_or_create(
            user=user,
            meeting=m1,
            task="Implement AI client wrapper and mock fallback validation",
            defaults={
                'owner': 'Sarah Connor',
                'due_date': today + timedelta(days=1),
                'priority': 'HIGH',
                'status': 'OPEN'
            }
        )

        ActionItem.objects.get_or_create(
            user=user,
            meeting=m1,
            task="Check customer demand for multi-language transcript support",
            defaults={
                'owner': 'Michael Chen',
                'due_date': today - timedelta(days=1),  # Overdue demo item
                'priority': 'MEDIUM',
                'status': 'OPEN'
            }
        )

        # 3. Meeting 2: Client Review
        m2, _ = Meeting.objects.get_or_create(
            user=user,
            title="Enterprise Client Alpha Delivery & Sign-off",
            defaults={
                'date': today - timedelta(days=5),
                'meeting_type': 'client',
                'participants': 'Alex Rivera, Rachel Green, Tom Vance',
                'transcript': """Alex Rivera: Thank you Tom for joining. Today we want to review the Alpha release and get alignment on Phase 2 deliverables.
Tom Vance (Client): The automated action tracker has already saved our teams substantial meeting overhead. We agreed to proceed with full rollout next month.
Rachel Green: Excellent. Alex, could you send over the updated Statement of Work (SOW)?
Alex Rivera: Yes, I will prepare the revised SOW and send it for client signature by Wednesday.
Rachel Green: I will coordinate with DevOps to ensure 99.9% uptime SLA compliance.
Tom Vance: Is there any risk of delay with the SOC2 compliance checklist?
Rachel Green: We are tracking all SOC2 controls actively and expect signoff next week."""
            }
        )

        insights_2 = generate_mock_insights(m2.title, m2.transcript, m2.participants, m2.get_meeting_type_display())
        MeetingInsight.objects.update_or_create(
            meeting=m2,
            defaults={
                'summary': insights_2['summary'],
                'discussion_points': insights_2['discussion_points'],
                'key_decisions': insights_2['key_decisions'],
                'risks_and_concerns': insights_2['risks_and_concerns'],
                'unanswered_questions': insights_2['unanswered_questions'],
                'raw_ai_response': insights_2,
                'ai_provider': 'mock'
            }
        )

        ActionItem.objects.get_or_create(
            user=user,
            meeting=m2,
            task="Prepare revised SOW and send for client signature",
            defaults={
                'owner': 'Alex Rivera',
                'due_date': today + timedelta(days=4),
                'priority': 'HIGH',
                'status': 'OPEN'
            }
        )

        ActionItem.objects.get_or_create(
            user=user,
            meeting=m2,
            task="Coordinate with DevOps for 99.9% SLA compliance audit",
            defaults={
                'owner': 'Rachel Green',
                'due_date': today + timedelta(days=7),
                'priority': 'MEDIUM',
                'status': 'IN_PROGRESS'
            }
        )

        # Standalone Action Item
        ActionItem.objects.get_or_create(
            user=user,
            meeting=None,
            task="Perform quarterly security certificate rotation",
            defaults={
                'owner': 'Unassigned',
                'due_date': None,
                'priority': 'LOW',
                'status': 'OPEN'
            }
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded demo user, meetings, AI insights, and action items!"))
