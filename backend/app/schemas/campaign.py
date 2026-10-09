import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import CampaignStatus


class CampaignCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    target_industry: str | None = Field(default=None, max_length=200)
    target_location: str | None = Field(default=None, max_length=200)
    target_company_size: str | None = Field(default=None, max_length=100)
    keywords: list[str] = Field(default_factory=list)


class CampaignUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    status: CampaignStatus | None = None
    target_industry: str | None = Field(default=None, max_length=200)
    target_location: str | None = Field(default=None, max_length=200)
    target_company_size: str | None = Field(default=None, max_length=100)
    keywords: list[str] | None = None


class CampaignOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    description: str | None = None
    status: CampaignStatus = CampaignStatus.DRAFT
    target_industry: str | None = None
    target_location: str | None = None
    target_company_size: str | None = None
    keywords: list[str] = []
    created_at: datetime
    updated_at: datetime
