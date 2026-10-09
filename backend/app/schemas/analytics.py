from pydantic import BaseModel


class AnalyticsOverview(BaseModel):
    total_leads: int = 0
    qualified_leads: int = 0
    hot_leads: int = 0
    contacted_leads: int = 0
    replies: int = 0
    positive_replies: int = 0
    meetings: int = 0
    conversions: int = 0
    do_not_contact: int = 0
    qualification_rate: float = 0.0
    reply_rate: float = 0.0
    conversion_rate: float = 0.0
    campaign_performance: list[dict] = []
    agent_success_rate: float | None = None
    agent_runs_total: int = 0
    agent_runs_failed: int = 0
