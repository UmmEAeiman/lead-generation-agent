"""Structured results returned by agents (validated before persistence)."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class DiscoveryResult(BaseModel):
    leads: list[dict[str, Any]] = Field(default_factory=list)
    provider: str = "unknown"
    selected: int = 0
    notes: str = ""
    used_llm: bool = False


class EnrichmentResult(BaseModel):
    fields: dict[str, Any] = Field(default_factory=dict)
    field_confidence: dict[str, str] = Field(default_factory=dict)
    used_llm: bool = False


class ResearchResult(BaseModel):
    summary: str = ""
    findings: list[dict[str, Any]] = Field(default_factory=list)
    pain_points: list[str] = Field(default_factory=list)
    buying_signals: list[str] = Field(default_factory=list)
    used_llm: bool = False


class QualificationResult(BaseModel):
    score: int = Field(ge=0, le=100)
    category: Literal["low", "medium", "high"] = "low"
    breakdown: dict[str, int] = Field(default_factory=dict)
    reasons: list[str] = Field(default_factory=list)
    confidence: str = "unknown"
    used_llm: bool = False


class PersonalizationResult(BaseModel):
    subject: str
    message: str
    used_facts: list[str] = Field(default_factory=list)
    omitted_info: list[str] = Field(default_factory=list)
    used_llm: bool = False


class FollowupResult(BaseModel):
    state: str
    action: Literal["follow_up", "wait", "stop", "confirm"]
    message: str | None = None
    reason: str
    used_llm: bool = False
