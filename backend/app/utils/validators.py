"""Shared input validation helpers."""

from app.models.enums import FollowupState, LeadStatus

LEAD_STATUSES = {s.value for s in LeadStatus}
FOLLOWUP_STATES = {s.value for s in FollowupState}

# Transition rules: DO_NOT_CONTACT is terminal; CONVERTED/REJECTED terminal too.
ALLOWED_STATUS_TRANSITIONS: dict[str, set[str]] = {
    LeadStatus.NEW.value: {
        LeadStatus.ENRICHING.value,
        LeadStatus.QUALIFIED.value,
        LeadStatus.UNQUALIFIED.value,
        LeadStatus.CONTACTED.value,
        LeadStatus.REJECTED.value,
        LeadStatus.DO_NOT_CONTACT.value,
    },
    LeadStatus.ENRICHING.value: {
        LeadStatus.QUALIFIED.value,
        LeadStatus.UNQUALIFIED.value,
        LeadStatus.CONTACTED.value,
        LeadStatus.REJECTED.value,
        LeadStatus.DO_NOT_CONTACT.value,
    },
    LeadStatus.QUALIFIED.value: {
        LeadStatus.CONTACTED.value,
        LeadStatus.UNQUALIFIED.value,
        LeadStatus.REJECTED.value,
        LeadStatus.DO_NOT_CONTACT.value,
    },
    LeadStatus.UNQUALIFIED.value: {LeadStatus.QUALIFIED.value, LeadStatus.DO_NOT_CONTACT.value},
    LeadStatus.CONTACTED.value: {
        LeadStatus.REPLIED.value,
        LeadStatus.DO_NOT_CONTACT.value,
    },
    LeadStatus.REPLIED.value: {
        LeadStatus.INTERESTED.value,
        LeadStatus.MEETING_BOOKED.value,
        LeadStatus.REJECTED.value,
        LeadStatus.DO_NOT_CONTACT.value,
    },
    LeadStatus.INTERESTED.value: {
        LeadStatus.MEETING_BOOKED.value,
        LeadStatus.CONVERTED.value,
        LeadStatus.DO_NOT_CONTACT.value,
    },
    LeadStatus.MEETING_BOOKED.value: {
        LeadStatus.CONVERTED.value,
        LeadStatus.REJECTED.value,
        LeadStatus.DO_NOT_CONTACT.value,
    },
    LeadStatus.CONVERTED.value: set(),
    LeadStatus.REJECTED.value: set(),
    LeadStatus.DO_NOT_CONTACT.value: set(),
}


def can_transition(current: str, new: str) -> bool:
    if current == new:
        return True
    return new in ALLOWED_STATUS_TRANSITIONS.get(current, set())


def is_terminal_status(status: str) -> bool:
    return status == LeadStatus.DO_NOT_CONTACT.value


def safe_ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)
