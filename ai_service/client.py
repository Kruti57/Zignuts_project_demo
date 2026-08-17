"""
Unified AI Client for Meeting Insights.
Supports Gemini API, OpenAI API, and intelligent structured Mock fallback.
"""

import json
import logging
import re
from typing import Dict, Any, Tuple
from django.conf import settings

from .prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from .validators import validate_and_clean_insights
from .mock_ai import generate_mock_insights

logger = logging.getLogger(__name__)


def strip_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    text = re.sub(r'<br\s*/?>', '\n', raw_html, flags=re.IGNORECASE)
    text = re.sub(r'</?(p|div|li|h[1-6]|tr|blockquote)[^>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#039;', "'")
    return text.strip()


class AIServiceClient:
    def __init__(self):
        self.gemini_key = getattr(settings, 'GEMINI_API_KEY', '').strip()
        self.openai_key = getattr(settings, 'OPENAI_API_KEY', '').strip()
        self.provider_pref = getattr(settings, 'AI_PROVIDER', 'auto').lower().strip()

    def generate_insights(self, title: str, transcript: str, participants: str = "", meeting_type: str = "", date: str = "") -> Tuple[Dict[str, Any], str]:
        """
        Generates structured insights from meeting transcript.
        Returns: (insights_dict, provider_name)
        """
        cleaned_transcript = strip_html(transcript)

        # If no transcript content, return mock defaults
        if not cleaned_transcript:
            mock_data = generate_mock_insights(title, "No transcript provided.", participants, meeting_type)
            _, cleaned, _ = validate_and_clean_insights(mock_data)
            return cleaned, 'mock'

        # 1. Try Gemini if configured
        if self.gemini_key and (self.provider_pref in ('gemini', 'auto')):
            try:
                insights, ok = self._call_gemini(title, cleaned_transcript, participants, meeting_type, date)
                if ok:
                    is_valid, cleaned, _ = validate_and_clean_insights(insights)
                    if is_valid:
                        return cleaned, 'gemini'
            except Exception as e:
                logger.warning(f"Gemini API call failed: {e}. Falling back...")

        # 2. Try OpenAI if configured
        if self.openai_key and (self.provider_pref in ('openai', 'auto')):
            try:
                insights, ok = self._call_openai(title, cleaned_transcript, participants, meeting_type, date)
                if ok:
                    is_valid, cleaned, _ = validate_and_clean_insights(insights)
                    if is_valid:
                        return cleaned, 'openai'
            except Exception as e:
                logger.warning(f"OpenAI API call failed: {e}. Falling back...")

        # 3. Intelligent Mock AI Fallback
        logger.info("Using intelligent Mock AI service for insights.")
        mock_data = generate_mock_insights(title, cleaned_transcript, participants, meeting_type)
        is_valid, cleaned, _ = validate_and_clean_insights(mock_data)
        return cleaned, 'mock'

    def _call_gemini(self, title: str, transcript: str, participants: str, meeting_type: str, date: str) -> Tuple[Dict[str, Any], bool]:
        import google.generativeai as genai
        genai.configure(api_key=self.gemini_key)

        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=SYSTEM_PROMPT,
            generation_config={"response_mime_type": "application/json"}
        )

        user_content = USER_PROMPT_TEMPLATE.format(
            title=title,
            date=date,
            meeting_type=meeting_type,
            participants=participants,
            transcript=transcript[:15000] # Safe token limit
        )

        response = model.generate_content(user_content)
        raw_text = response.text.strip()
        data = self._parse_json(raw_text)
        return data, bool(data)

    def _call_openai(self, title: str, transcript: str, participants: str, meeting_type: str, date: str) -> Tuple[Dict[str, Any], bool]:
        from openai import OpenAI
        client = OpenAI(api_key=self.openai_key)

        user_content = USER_PROMPT_TEMPLATE.format(
            title=title,
            date=date,
            meeting_type=meeting_type,
            participants=participants,
            transcript=transcript[:15000]
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )

        raw_text = response.choices[0].message.content.strip()
        data = self._parse_json(raw_text)
        return data, bool(data)

    def _parse_json(self, text: str) -> Dict[str, Any]:
        """Extracts and parses JSON string safely."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Clean markdown codeblocks if present
            cleaned = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
            cleaned = re.sub(r'```$', '', cleaned, flags=re.MULTILINE).strip()
            try:
                return json.loads(cleaned)
            except Exception:
                return {}
