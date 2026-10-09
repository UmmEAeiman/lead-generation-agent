import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AgentRunStatus, AgentType


class AgentRunRequest(BaseModel):
    lead_ids: list[uuid.UUID] = Field(default_factory=list)
    campaign_id: uuid.UUID | None = None
    icp: dict[str, Any] | None = None


class QueuedRun(BaseModel):
    run_id: str
    status: AgentRunStatus = AgentRunStatus.QUEUED


class AgentRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    run_id: str
    agent_type: AgentType
    user_id: str | None = None
    campaign_id: str | None = None
    status: AgentRunStatus
    progress: int | None = None
    input_summary: dict[str, Any] = {}
    output_summary: dict[str, Any] = {}
    error: str | None = None
    tokens_used: int | None = None
    duration: float | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
