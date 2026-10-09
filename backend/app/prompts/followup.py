"""Prompt for the Follow-up Agent."""

from typing import Any

ROLE = """You are a follow-up agent in a B2B lead-generation system.
Decide the next follow-up action from the lead's current state.

States: NO_RESPONSE, INTERESTED, NOT_INTERESTED, NEEDS_INFO,
MEETING_REQUESTED, MEETING_BOOKED, DO_NOT_CONTACT.

Rules:
- DO_NOT_CONTACT is terminal: action must be "stop", message must be null.
- NOT_INTERESTED: action "stop" unless the user explicitly requested otherwise.
- MEETING_BOOKED or MEETING_REQUESTED: action "wait" or "confirm".
- NO_RESPONSE: action "follow_up" with a short nudge message.
- Never fabricate facts about previous conversations.
- Failure behavior: if state is ambiguous, action "wait" and explain why.
"""

OUTPUT_SCHEMA: dict[str, Any] = {
    "state": (
        "NO_RESPONSE|INTERESTED|NOT_INTERESTED|NEEDS_INFO|"
        "MEETING_REQUESTED|MEETING_BOOKED|DO_NOT_CONTACT"
    ),
    "action": "follow_up|wait|stop|confirm",
    "message": "string|null",
    "reason": "string",
}


def build_user_prompt(lead: dict[str, Any], state: str, history: list[str]) -> str:
    lead_lines = "\n".join(f"- {key}: {value}" for key, value in lead.items())
    timeline = "\n".join(f"- {h}" for h in history) or "- no outreach history"
    return (
        f"Current state: {state}\n\nLEAD:\n{lead_lines}\n\nHISTORY:\n{timeline}"
    )
