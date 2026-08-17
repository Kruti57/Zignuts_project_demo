from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from meetings.models import Meeting, MeetingInsight
from actions.models import ActionItem
from ai_service.mock_ai import generate_mock_insights


class Command(BaseCommand):
    help = "Seeds initial demo user and exclusively the Zignuts AI assessment meeting, insights, and actions"

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
            self.stdout.write(self.style.WARNING(f"Demo user '{username}' found. Refreshing exclusively to Zignuts data..."))

        # Clear any old generic meetings and actions for demo user
        ActionItem.objects.filter(user=user).delete()
        Meeting.objects.filter(user=user).delete()

        today = timezone.localdate()

        # 2. Main Zignuts Assessment Primary Demo Meeting
        m1 = Meeting.objects.create(
            user=user,
            title="Zignuts AI Platform Architecture & Sprint Deliverables Review",
            date=today - timedelta(days=1),
            meeting_type='sprint',
            participants="Sarah Connor (Tech Lead), David Kim (Backend Lead), Elena Rostova (Frontend Lead), Michael Chen (Product Manager)",
            transcript="""Sarah Connor (Tech Lead): Welcome everyone. Our main goal for this sprint is closing the customer onboarding bottleneck and finalizing the AI Meeting Notes integration.
David Kim (Backend Lead): On the backend architecture, Sarah and I reviewed the schema. We decided to use MySQL with PyMySQL connection pooling for high throughput. I will finalize the database migration scripts and set up the DRF endpoints by Friday.
Elena Rostova (Frontend Lead): On the frontend, I am building the modern SaaS dashboard and the Action Tracker. I will complete the Quill rich text editor and the dark mode theme by Thursday.
Michael Chen (Product Manager): Great. Sarah, what about the AI service fallback?
Sarah Connor: We agreed that if the Gemini API key is missing or rate limited, the system must seamlessly fall back to an intelligent structured mock AI without throwing errors. I will write the AI client wrapper and validation tests by tomorrow.
David Kim: One concern: what if the external webhook experiences latency during action item sync?
Sarah Connor: That is a potential risk. We should add retry logic and timeout limits.
Elena Rostova: Michael, do we need multi-language transcript support in this phase?
Michael Chen: That is an open question. Let's verify customer demand before scoping it for next quarter."""
        )

        insights_1 = generate_mock_insights(m1.title, m1.transcript, m1.participants, m1.get_meeting_type_display())
        MeetingInsight.objects.create(
            meeting=m1,
            summary=insights_1['summary'],
            discussion_points=insights_1['discussion_points'],
            key_decisions=insights_1['key_decisions'],
            risks_and_concerns=insights_1['risks_and_concerns'],
            unanswered_questions=insights_1['unanswered_questions'],
            raw_ai_response=insights_1,
            ai_provider='mock'
        )

        # Action Items extracted exclusively from the Zignuts Meeting
        ActionItem.objects.create(
            user=user,
            meeting=m1,
            task="Finalize database migrations and DRF endpoints",
            owner="David Kim",
            due_date=today + timedelta(days=3),
            priority="HIGH",
            status="IN_PROGRESS"
        )

        ActionItem.objects.create(
            user=user,
            meeting=m1,
            task="Build modern SaaS dashboard and action tracker UI",
            owner="Elena Rostova",
            due_date=today + timedelta(days=2),
            priority="HIGH",
            status="COMPLETED"
        )

        ActionItem.objects.create(
            user=user,
            meeting=m1,
            task="Implement AI client wrapper and mock fallback validation",
            owner="Sarah Connor",
            due_date=today + timedelta(days=1),
            priority="HIGH",
            status="OPEN"
        )

        ActionItem.objects.create(
            user=user,
            meeting=m1,
            task="Check customer demand for multi-language transcript support",
            owner="Michael Chen",
            due_date=today - timedelta(days=1),  # Overdue item for evaluation
            priority="MEDIUM",
            status="OPEN"
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded exclusively Zignuts AI assessment data!"))
