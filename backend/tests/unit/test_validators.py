from app.models.enums import LeadStatus
from app.utils.validators import can_transition, is_terminal_status, safe_ratio


def test_dnc_is_terminal() -> None:
    status = LeadStatus.DO_NOT_CONTACT.value
    assert is_terminal_status(status)
    assert not can_transition(status, LeadStatus.CONTACTED.value)
    assert not can_transition(status, LeadStatus.QUALIFIED.value)


def test_valid_transition() -> None:
    assert can_transition(LeadStatus.NEW.value, LeadStatus.ENRICHING.value)
    assert can_transition(LeadStatus.QUALIFIED.value, LeadStatus.CONTACTED.value)


def test_invalid_transition() -> None:
    assert not can_transition(LeadStatus.NEW.value, LeadStatus.MEETING_BOOKED.value)
    assert not can_transition(LeadStatus.CONVERTED.value, LeadStatus.CONTACTED.value)


def test_same_status_allowed() -> None:
    assert can_transition(LeadStatus.CONTACTED.value, LeadStatus.CONTACTED.value)


def test_safe_ratio() -> None:
    assert safe_ratio(1, 4) == 25.0
    assert safe_ratio(0, 0) == 0.0
