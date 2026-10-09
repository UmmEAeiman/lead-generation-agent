import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import OutreachStatus


class OutreachPrepareRequest(BaseModel):
    lead_id: uuid.UUID
    campaign_id: uuid.UUID | None = None
    channel: str = Field(default="email", pattern="^(email)$")


class OutreachOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    lead_id: uuid.UUID
    campaign_id: uuid.UUID | None = None
    owner_id: uuid.UUID
    channel: str
    subject: str | None = None
    body: str
    status: OutreachStatus = OutreachStatus.PREPARED
    error: str | None = None
    approved_at: datetime | None = None
    sent_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
