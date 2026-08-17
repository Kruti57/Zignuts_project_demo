"""
Intelligent Mock AI Service for AI Meeting Notes & Action Tracker.
Provides high-fidelity, contextual natural language extraction without requiring an API key.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Any, List


def strip_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    text = re.sub(r'<br\s*/?>', '\n', raw_html, flags=re.IGNORECASE)
    text = re.sub(r'</?(p|div|li|h[1-6]|tr|blockquote)[^>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#039;', "'")
    return text


def generate_mock_insights(title: str, transcript: str, participants: str = "", meeting_type: str = "") -> Dict[str, Any]:
    """
    Parses meeting transcript to generate realistic, structured insights
    matching the schema expected from Gemini/OpenAI.
    """
    text = strip_html(transcript).strip()
    participant_list = [p.strip() for p in participants.split(',') if p.strip()]
    
    # Split transcript into lines and sentences
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    sentences = []
    for line in lines:
        for s in re.split(r'(?<=[.!?])\s+', line):
            s_clean = s.strip()
            if len(s_clean) > 5:
                sentences.append(s_clean)

    # 1. Extract Action Items
    action_items: List[Dict[str, str]] = []
    action_verbs = ['will', 'shall', 'to do', 'todo', 'action item', 'need to', 'must', 'responsible for', 'take care of', 'follow up', 'deploy', 'fix', 'implement', 'review', 'prepare', 'schedule', 'write', 'create', 'update']
    
    # Check lines and sentences for action patterns
    for line in lines:
        speaker_match = re.match(r'^([A-Za-z0-9\s]+?):\s*(.+)$', line)
        speaker = speaker_match.group(1).strip() if speaker_match else ""
        content = speaker_match.group(2).strip() if speaker_match else line

        content_lower = content.lower()
        if any(verb in content_lower for verb in action_verbs) or "action:" in content_lower or "todo:" in content_lower:
            # Detect owner
            owner = "Unassigned"
            if speaker and speaker in participant_list:
                owner = speaker
            else:
                for p in participant_list:
                    if p.lower() in content_lower:
                        owner = p
                        break
                if owner == "Unassigned" and speaker:
                    owner = speaker

            # Detect due date
            due_date = "Not specified"
            today = datetime.now()
            if "by friday" in content_lower:
                days_ahead = 4 - today.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                due_date = (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
            elif "by monday" in content_lower:
                days_ahead = (0 - today.weekday()) % 7
                if days_ahead == 0:
                    days_ahead = 7
                due_date = (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
            elif "by tomorrow" in content_lower:
                due_date = (today + timedelta(days=1)).strftime('%Y-%m-%d')
            elif "by next week" in content_lower or "next sprint" in content_lower:
                due_date = (today + timedelta(days=7)).strftime('%Y-%m-%d')
            elif "by end of day" in content_lower or "today" in content_lower:
                due_date = today.strftime('%Y-%m-%d')
            else:
                # Regex for explicit YYYY-MM-DD or MM/DD/YYYY
                date_match = re.search(r'\b(20\d{2}[-/]\d{1,2}[-/]\d{1,2})\b', content)
                if date_match:
                    due_date = date_match.group(1).replace('/', '-')

            # Detect priority
            priority = "MEDIUM"
            if any(w in content_lower for w in ['urgent', 'critical', 'asap', 'high priority', 'blocker', 'immediately']):
                priority = "HIGH"
            elif any(w in content_lower for w in ['low priority', 'nice to have', 'whenever', 'optional', 'later']):
                priority = "LOW"

            # Clean task text
            task_clean = re.sub(r'^(action item:?|todo:?|\-|\*)\s*', '', content, flags=re.IGNORECASE).strip()
            if len(task_clean) > 8:
                action_items.append({
                    "task": task_clean,
                    "owner": owner if owner else "Unassigned",
                    "due_date": due_date,
                    "priority": priority
                })

    # Default action items if none explicitly detected
    if not action_items:
        if participant_list:
            p1 = participant_list[0]
            action_items.append({
                "task": f"Review meeting notes and coordinate next steps for {title}",
                "owner": p1,
                "due_date": (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
                "priority": "HIGH"
            })
            if len(participant_list) > 1:
                p2 = participant_list[1]
                action_items.append({
                    "task": f"Prepare follow-up documentation and deliverables",
                    "owner": p2,
                    "due_date": (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
                    "priority": "MEDIUM"
                })
        else:
            action_items.append({
                "task": f"Finalize documentation and action plan for {title}",
                "owner": "Unassigned",
                "due_date": "Not specified",
                "priority": "MEDIUM"
            })

    # 2. Extract Key Decisions
    key_decisions = []
    decision_keywords = ['decided', 'agreed', 'approved', 'consensus', 'going with', 'chosen', 'selected', 'confirmed', 'finalized']
    for s in sentences:
        s_lower = s.lower()
        if any(dk in s_lower for dk in decision_keywords) and len(s) > 15:
            clean_decision = re.sub(r'^(we\s+)?(agreed\s+that|decided\s+to|decided\s+that)\s*', '', s, flags=re.IGNORECASE).strip()
            clean_decision = clean_decision[0].upper() + clean_decision[1:] if clean_decision else s
            if clean_decision not in key_decisions:
                key_decisions.append(clean_decision)

    if not key_decisions:
        key_decisions = [
            f"Approved strategy and alignment regarding {title.lower()}.",
            "Agreed on milestone timeline and individual team responsibilities."
        ]

    # 3. Extract Discussion Points
    discussion_points = []
    for line in lines[:8]:
        speaker_match = re.match(r'^([A-Za-z0-9\s]+?):\s*(.+)$', line)
        if speaker_match:
            discussion_points.append(f"{speaker_match.group(1)}: {speaker_match.group(2)[:120]}")
        elif len(line) > 20 and not line.startswith('#'):
            discussion_points.append(line[:130])

    if len(discussion_points) < 2:
        discussion_points = [
            f"Reviewed current status and objectives for {title}.",
            "Evaluated timeline constraints, resource allocation, and key deliverables.",
            "Discussed team handoffs and communication workflows."
        ]
    else:
        discussion_points = discussion_points[:5]

    # 4. Extract Risks and Concerns
    risks_and_concerns = []
    risk_keywords = ['risk', 'concern', 'blocker', 'delay', 'issue', 'challenge', 'bottleneck', 'worry', 'threat', 'constraint']
    for s in sentences:
        s_lower = s.lower()
        if any(rk in s_lower for rk in risk_keywords) and len(s) > 15:
            if s not in risks_and_concerns:
                risks_and_concerns.append(s)

    if not risks_and_concerns:
        risks_and_concerns = [
            "Potential timeline slippage if external dependencies or approvals are delayed.",
            "Resource bandwidth constraints during high-priority deliverables."
        ]

    # 5. Extract Unanswered Questions
    unanswered_questions = []
    for s in sentences:
        if s.strip().endswith('?') and len(s) > 10:
            if s not in unanswered_questions:
                unanswered_questions.append(s)

    if not unanswered_questions:
        unanswered_questions = [
            "What is the final sign-off deadline for the upcoming milestone?",
            "Do we need additional third-party licenses or cloud infrastructure budget?"
        ]

    # 6. Executive Summary
    participant_summary = f" with {', '.join(participant_list)}" if participant_list else ""
    summary_text = (
        f"The {meeting_type or 'team'} session on '{title}' focused on evaluating project milestones, team alignment, and execution requirements{participant_summary}. "
        f"Key outcomes were established with {len(key_decisions)} major decision(s) made and {len(action_items)} designated action item(s). "
        f"The team reviewed critical risks and outlined clear ownership to maintain operational velocity."
    )

    return {
        "summary": summary_text,
        "discussion_points": discussion_points,
        "key_decisions": key_decisions,
        "action_items": action_items,
        "risks_and_concerns": risks_and_concerns,
        "unanswered_questions": unanswered_questions
    }
