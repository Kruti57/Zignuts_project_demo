from django.test import TestCase
from ai_service.mock_ai import generate_mock_insights
from ai_service.validators import validate_and_clean_insights
from ai_service.client import AIServiceClient


class AIServiceTestCase(TestCase):
    def test_mock_ai_insights_structure(self):
        title = "Sprint Planning"
        transcript = """
        John: I will deploy the authentication service by Friday.
        Mary: We agreed to use PostgreSQL and Redis.
        John: Is there any risk with AWS quota limits?
        """
        data = generate_mock_insights(title, transcript, participants="John, Mary", meeting_type="Sprint")

        self.assertIn("summary", data)
        self.assertIn("discussion_points", data)
        self.assertIn("key_decisions", data)
        self.assertIn("action_items", data)
        self.assertIn("risks_and_concerns", data)
        self.assertIn("unanswered_questions", data)

        self.assertTrue(len(data["action_items"]) > 0)
        self.assertEqual(data["action_items"][0]["owner"], "John")

    def test_insights_validator_and_defaults(self):
        raw_output = {
            "summary": "Meeting went well.",
            "discussion_points": ["Point 1", "Point 2"],
            "key_decisions": ["Decision 1"],
            "action_items": [
                {"task": "Prepare report"}  # missing owner & due_date
            ],
            "risks_and_concerns": ["Risk 1"],
            "unanswered_questions": ["Question 1?"]
        }

        is_valid, cleaned, error = validate_and_clean_insights(raw_output)
        self.assertTrue(is_valid)
        self.assertEqual(cleaned["action_items"][0]["owner"], "Unassigned")
        self.assertEqual(cleaned["action_items"][0]["due_date"], "Not specified")
        self.assertEqual(cleaned["action_items"][0]["priority"], "MEDIUM")

    def test_ai_client_fallback(self):
        client = AIServiceClient()
        data, provider = client.generate_insights(
            title="Design Review",
            transcript="Alice: I will redesign the modal by tomorrow.",
            participants="Alice",
            meeting_type="Design"
        )
        self.assertIn("summary", data)
        self.assertIn("action_items", data)
        self.assertTrue(provider in ('mock', 'gemini', 'openai'))
