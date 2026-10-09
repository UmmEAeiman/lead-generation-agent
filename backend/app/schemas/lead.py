import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.enums import DataConfidence, FollowupState, LeadStatus

Qualification = Literal["low", "medium", "high", "unknown"]


class LeadBase(BaseModel):
    company_name: str = Field(min_length=1, max_length=300)
    website: str | None = Field(default=None, max_length=500)
    industry: str | None = Field(default=None, max_length=200)
    location: str | None = Field(default=None, max_length=200)
    company_size: str | None = Field(default=None, max_length=100)
    contact_name: str | None = Field(default=None, max_length=200)
    contact_role: str | None = Field(default=None, max_length=200)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    linkedin_url: str | None = Field(default=None, max_length=500)
    source: str | None = Field(default=None, max_length=100)
    source_url: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=5000)


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    company_name: str | None = Field(default=None, min_length=1, max_length=300)
    website: str | None = Field(default=None, max_length=500)
    industry: str | None = Field(default=None, max_length=200)
    location: str | None = Field(default=None, max_length=200)
    company_size: str | None = Field(default=None, max_length=100)
    contact_name: str | None = Field(default=None, max_length=200)
    contact_role: str | None = Field(default=None, max_length=200)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    linkedin_url: str | None = Field(default=None, max_length=500)
    source: str | None = Field(default=None, max_length=100)
    source_url: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=5000)
    status: LeadStatus | None = None
    followup_state: FollowupState | None = None

    @field_validator("status", "followup_state", mode="before")
    @classmethod
    def _to_value(cls, v: object) -> object:
        return v.value if hasattr(v, "value") else v


class LeadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: uuid.UUID
    company_name: str
    website: str | None = None
    industry: str | None = None
    location: str | None = None
    company_size: str | None = None
    contact_name: str | None = None
    contact_role: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    source: str | None = None
    source_url: str | None = None
    description: str | None = None
    lead_score: int | None = None
    qualification: Qualification = "unknown"
    qualification_reasons: list[str] = []
    status: LeadStatus = LeadStatus.NEW
    followup_state: FollowupState | None = None
    research_summary: str | None = None
    pain_points: list[str] = []
    personalized_message: str | None = None
    field_confidence: dict[str, DataConfidence | str] = {}
    created_at: datetime
    updated_at: datetime
