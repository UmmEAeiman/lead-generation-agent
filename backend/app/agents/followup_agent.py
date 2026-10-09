"""Follow-up Agent: decide the next outreach action from lead state."""

from typing import Any

from app.agents.base import BaseAgent
from app.agents.results import FollowupResult
from app.models.enums import FollowupState
from app.prompts import followup as prompt

_STATE_ACTIONS: dict[str, tuple[str, str]] = {
    FollowupState.DO_NOT_CONTACT.value: (
        "stop",
        "Lead opted out (DO_NOT_CONTACT): all automated outreach stops.",
    ),
    FollowupState.NOT_INTERESTED.value: (
        "stop",
        "Lead is not interested: no further outreach.",
    ),
    FollowupState.MEETING_BOOKED.value: (
        "confirm",
        "Meeting booked: send a confirmation and stop cold follow-ups.",
    ),
    FollowupState.MEETING_REQUESTED.value: (
        "confirm",
        "Meeting requested: reply to propose concrete times.",
    ),
    FollowupState.INTERESTED.value: (
        "follow_up",
        "Lead showed interest: propose a call.",
    ),
    FollowupState.NEEDS_INFO.value: (
        "follow_up",
        "Lead asked for information: send only the requested, verified details.",
    ),
    FollowupState.NO_RESPONSE.value: (
        "follow_up",
        "No response yet: send one polite follow-up.",
    ),
}

_MESSAGES: dict[str, str] = {
    FollowupState.NO_RESPONSE.value: (
        "Hi, just circling back on my previous note — if this isn't relevant right "
        "now, let me know and I'll close the loop."
    ),
    FollowupState.INTERESTED.value: (
        "Thanks for the reply. Would a short call this week work? I can share a "
        "couple of concrete ideas relevant to your team."
    ),
    FollowupState.NEEDS_INFO.value: (
        "Happy to send the details you asked for — could you confirm which "
        "specifics would be most useful so I can keep it focused?"
    ),
    FollowupState.MEETING_REQUESTED.value: (
        "Great — I'll put together a few time options and send them over shortly."
    ),
    FollowupState.MEETING_BOOKED.value: (
        "Confirming our meeting. I'll send an invite with the details shortly."
    ),
}


def state_from_lead_status(status: str) -> str:
    mapping = {
        "DO_NOT_CONTACT": FollowupState.DO_NOT_CONTACT.value,
        "REJECTED": FollowupState.NOT_INTERESTED.value,
        "MEETING_BOOKED": FollowupState.MEETING_BOOKED.value,
        "INTERESTED": FollowupState.INTERESTED.value,
        "REPLIED": FollowupState.INTERESTED.value,
        "CONTACTED": FollowupState.NO_RESPONSE.value,
        "CONVERTED": FollowupState.MEETING_BOOKED.value,
    }
    return mapping.get(status, FollowupState.NO_RESPONSE.value)


class FollowupAgent(BaseAgent):
    name = "followup"

    async def run(
        self,
        lead: dict[str, Any],
        state: str,
        history: list[str] | None = None,
    ) -> FollowupResult:
        state_key = state if state in _STATE_ACTIONS else FollowupState.NO_RESPONSE.value
        action, reason = _STATE_ACTIONS[state_key]

        if action == "stop":
            return FollowupResult(
                state=state_key,
                action="stop",
                message=None,
                reason=reason,
                used_llm=False,
            )

        base_message = _MESSAGES.get(state_key)

        response = await self.chat_json(
            system=prompt.ROLE,
            user=prompt.build_user_prompt(lead, state_key, history or []),
            output_schema=prompt.OUTPUT_SCHEMA,
        )
        if response and isinstance(response.get("message"), str) and response["message"].strip():
            response_action = response.get("action")
            final_action = (
                response_action
                if response_action in {"follow_up", "wait", "stop", "confirm"}
                else action
            )
            if final_action == "stop":
                return FollowupResult(
                    state=state_key,
                    action="stop",
                    message=None,
                    reason=str(response.get("reason") or reason)[:300],
                    used_llm=True,
                )
            return FollowupResult(
                state=state_key,
                action=final_action,  # type: ignore[arg-type]
                message=response["message"].strip()[:3000],
                reason=str(response.get("reason") or reason)[:300],
                used_llm=True,
            )

        return FollowupResult(
            state=state_key,
            action=action,  # type: ignore[arg-type]
            message=base_message,
            reason=reason,
            used_llm=False,
        )
