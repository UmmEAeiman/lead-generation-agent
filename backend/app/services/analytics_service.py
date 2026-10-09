"""Analytics computed from persisted data (never UI-side guesses)."""

from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent_run import AgentRun
from app.models.campaign import Campaign
from app.models.enums import AgentRunStatus, LeadStatus
from app.models.lead import Lead
from app.schemas.analytics import AnalyticsOverview

_REPLIED = [
    LeadStatus.REPLIED.value,
    LeadStatus.INTERESTED.value,
    LeadStatus.MEETING_BOOKED.value,
    LeadStatus.CONVERTED.value,
]
_CONTACTED = [LeadStatus.CONTACTED.value, *_REPLIED]
_POSITIVE = [
    LeadStatus.INTERESTED.value,
    LeadStatus.MEETING_BOOKED.value,
    LeadStatus.CONVERTED.value,
]
_QUALIFIED = [
    LeadStatus.QUALIFIED.value,
    LeadStatus.CONTACTED.value,
    LeadStatus.REPLIED.value,
    LeadStatus.INTERESTED.value,
    LeadStatus.MEETING_BOOKED.value,
    LeadStatus.CONVERTED.value,
]


class AnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def overview(self, owner_id: UUID) -> AnalyticsOverview:
        status_counts_stmt = (
            select(Lead.status, func.count(Lead.id))
            .where(Lead.owner_id == owner_id)
            .group_by(Lead.status)
        )
        rows = (await self.session.execute(status_counts_stmt)).all()
        counts = {status: count for status, count in rows}
        total = sum(counts.values())

        def count_for(statuses: list[str]) -> int:
            return sum(counts.get(status, 0) for status in statuses)

        contacted = count_for(_CONTACTED)
        replies = count_for(_REPLIED)
        positive = count_for(_POSITIVE)
        qualified = count_for(_QUALIFIED)
        hot = 0
        if total:
            hot_stmt = select(func.count(Lead.id)).where(
                Lead.owner_id == owner_id,
                Lead.lead_score >= 70,
                Lead.status.notin_([LeadStatus.REJECTED.value, LeadStatus.UNQUALIFIED.value]),
            )
            hot = int((await self.session.execute(hot_stmt)).scalar_one())

        campaigns_stmt = (
            select(
                Campaign.id,
                Campaign.name,
                func.count(Lead.id).label("total_leads"),
                func.sum(
                    case((Lead.status == LeadStatus.QUALIFIED.value, 1), else_=0)
                ).label("qualified"),
                func.sum(case((Lead.status.in_(_CONTACTED), 1), else_=0)).label("contacted"),
                func.sum(case((Lead.status.in_(_REPLIED), 1), else_=0)).label("replies"),
                func.sum(case((Lead.status == LeadStatus.CONVERTED.value, 1), else_=0)).label(
                    "conversions"
                ),
            )
            .select_from(Campaign)
            .outerjoin(Lead, Lead.campaign_id == Campaign.id)
            .where(Campaign.owner_id == owner_id)
            .group_by(Campaign.id, Campaign.name)
            .order_by(Campaign.created_at.desc())
        )
        campaign_rows = (await self.session.execute(campaigns_stmt)).all()
        campaign_performance = [
            {
                "campaign_id": str(row.id),
                "name": row.name,
                "total_leads": int(row.total_leads or 0),
                "qualified": int(row.qualified or 0),
                "contacted": int(row.contacted or 0),
                "replies": int(row.replies or 0),
                "conversions": int(row.conversions or 0),
            }
            for row in campaign_rows
        ]

        runs_stmt = select(
            func.count(AgentRun.run_id),
            func.sum(case((AgentRun.status == AgentRunStatus.FAILED.value, 1), else_=0)),
        ).where(AgentRun.user_id == str(owner_id))
        runs_row = (await self.session.execute(runs_stmt)).one()
        runs_total = int(runs_row[0] or 0)
        runs_failed = int(runs_row[1] or 0)
        completed = runs_total - runs_failed
        success_rate = round((completed / runs_total) * 100, 2) if runs_total else None

        def rate(num: int, den: int) -> float:
            return round((num / den) * 100, 2) if den else 0.0

        return AnalyticsOverview(
            total_leads=total,
            qualified_leads=qualified,
            hot_leads=hot,
            contacted_leads=contacted,
            replies=replies,
            positive_replies=positive,
            meetings=counts.get(LeadStatus.MEETING_BOOKED.value, 0),
            conversions=counts.get(LeadStatus.CONVERTED.value, 0),
            do_not_contact=counts.get(LeadStatus.DO_NOT_CONTACT.value, 0),
            qualification_rate=rate(qualified, total),
            reply_rate=rate(replies, contacted),
            conversion_rate=rate(counts.get(LeadStatus.CONVERTED.value, 0), total),
            campaign_performance=campaign_performance,
            agent_success_rate=success_rate,
            agent_runs_total=runs_total,
            agent_runs_failed=runs_failed,
        )
