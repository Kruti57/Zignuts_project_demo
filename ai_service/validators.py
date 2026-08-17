"""
Validators and sanitizers for structured AI meeting insights.
"""

from typing import Dict, Any, Tuple


def validate_and_clean_insights(data: Any) -> Tuple[bool, Dict[str, Any], str]:
    """
    Validates and cleans structured AI insights output.
    Returns: (is_valid: bool, cleaned_data: dict, error_message: str)
    """
    if not isinstance(data, dict):
        return False, {}, "Output must be a JSON object/dictionary."

    cleaned: Dict[str, Any] = {
        "summary": "",
        "discussion_points": [],
        "key_decisions": [],
        "action_items": [],
        "risks_and_concerns": [],
        "unanswered_questions": [],
    }

    # 1. Summary
    summary = data.get("summary", "")
    if isinstance(summary, str):
        cleaned["summary"] = summary.strip()
    elif isinstance(summary, list):
        cleaned["summary"] = " ".join(str(s) for s in summary)
    else:
        cleaned["summary"] = str(summary or "")

    # 2. Discussion Points
    dp = data.get("discussion_points", [])
    if isinstance(dp, list):
        cleaned["discussion_points"] = [str(item).strip() for item in dp if str(item).strip()]
    elif isinstance(dp, str) and dp.strip():
        cleaned["discussion_points"] = [line.strip("- *• ") for line in dp.split("\n") if line.strip()]

    # 3. Key Decisions
    kd = data.get("key_decisions", [])
    if isinstance(kd, list):
        cleaned["key_decisions"] = [str(item).strip() for item in kd if str(item).strip()]
    elif isinstance(kd, str) and kd.strip():
        cleaned["key_decisions"] = [line.strip("- *• ") for line in kd.split("\n") if line.strip()]

    # 4. Action Items
    actions = data.get("action_items", [])
    cleaned_actions = []
    if isinstance(actions, list):
        for item in actions:
            if isinstance(item, dict):
                task = str(item.get("task", "")).strip()
                if not task:
                    continue
                owner = str(item.get("owner", "")).strip()
                if not owner or owner.lower() in ("none", "null", "unknown", "n/a", ""):
                    owner = "Unassigned"

                due_date = str(item.get("due_date", "")).strip()
                if not due_date or due_date.lower() in ("none", "null", "unknown", "n/a", "tbd", ""):
                    due_date = "Not specified"

                priority = str(item.get("priority", "MEDIUM")).upper().strip()
                if priority not in ("LOW", "MEDIUM", "HIGH"):
                    priority = "MEDIUM"

                cleaned_actions.append({
                    "task": task,
                    "owner": owner,
                    "due_date": due_date,
                    "priority": priority
                })
            elif isinstance(item, str) and item.strip():
                cleaned_actions.append({
                    "task": item.strip(),
                    "owner": "Unassigned",
                    "due_date": "Not specified",
                    "priority": "MEDIUM"
                })
    cleaned["action_items"] = cleaned_actions

    # 5. Risks and Concerns
    rc = data.get("risks_and_concerns", [])
    if isinstance(rc, list):
        cleaned["risks_and_concerns"] = [str(item).strip() for item in rc if str(item).strip()]
    elif isinstance(rc, str) and rc.strip():
        cleaned["risks_and_concerns"] = [line.strip("- *• ") for line in rc.split("\n") if line.strip()]

    # 6. Unanswered Questions
    uq = data.get("unanswered_questions", [])
    if isinstance(uq, list):
        cleaned["unanswered_questions"] = [str(item).strip() for item in uq if str(item).strip()]
    elif isinstance(uq, str) and uq.strip():
        cleaned["unanswered_questions"] = [line.strip("- *• ") for line in uq.split("\n") if line.strip()]

    return True, cleaned, ""
