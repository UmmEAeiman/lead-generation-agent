from enum import StrEnum


class LeadStatus(StrEnum):
    NEW = "NEW"
    ENRICHING = "ENRICHING"
    QUALIFIED = "QUALIFIED"
    UNQUALIFIED = "UNQUALIFIED"
    CONTACTED = "CONTACTED"
    REPLIED = "REPLIED"
    INTERESTED = "INTERESTED"
    MEETING_BOOKED = "MEETING_BOOKED"
    CONVERTED = "CONVERTED"
    REJECTED = "REJECTED"
    DO_NOT_CONTACT = "DO_NOT_CONTACT"


class QualificationLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class CampaignStatus(StrEnum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"


class OutreachStatus(StrEnum):
    PREPARED = "PREPARED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    SENT = "SENT"
    FAILED = "FAILED"
    REPLIED = "REPLIED"
    OPTED_OUT = "OPTED_OUT"


class FollowupState(StrEnum):
    NO_RESPONSE = "NO_RESPONSE"
    INTERESTED = "INTERESTED"
    NOT_INTERESTED = "NOT_INTERESTED"
    NEEDS_INFO = "NEEDS_INFO"
    MEETING_REQUESTED = "MEETING_REQUESTED"
    MEETING_BOOKED = "MEETING_BOOKED"
    DO_NOT_CONTACT = "DO_NOT_CONTACT"


class AgentType(StrEnum):
    DISCOVERY = "discovery"
    ENRICHMENT = "enrichment"
    RESEARCH = "research"
    QUALIFICATION = "qualification"
    PERSONALIZATION = "personalization"
    FOLLOWUP = "followup"
    PIPELINE = "pipeline"


class AgentRunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DataConfidence(StrEnum):
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    UNKNOWN = "unknown"
