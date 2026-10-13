from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.outreach import Outreach


class OutreachRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, outreach_id: UUID, owner_id: UUID) -> Outreach | None:
        result = await self.session.execute(
            select(Outreach).where(Outreach.id == outreach_id, Outreach.owner_id == owner_id)
        )
        return result.scalar_one_or_none()

    async def latest_for_lead(self, lead_id: UUID, owner_id: UUID) -> Outreach | None:
        result = await self.session.execute(
            select(Outreach)
            .where(Outreach.lead_id == lead_id, Outreach.owner_id == owner_id)
            .order_by(Outreach.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        owner_id: UUID,
        *,
        lead_id: UUID | None = None,
        status: str | None = None,
        run_id: str | None = None,
        campaign_id: UUID | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Outreach], int]:
        stmt = select(Outreach).where(Outreach.owner_id == owner_id)
        if lead_id:
            stmt = stmt.where(Outreach.lead_id == lead_id)
        if status:
            stmt = stmt.where(Outreach.status == status)
        if run_id:
            stmt = stmt.where(Outreach.run_id == run_id)
        if campaign_id:
            stmt = stmt.where(Outreach.campaign_id == campaign_id)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = int((await self.session.execute(count_stmt)).scalar_one())
        stmt = stmt.order_by(Outreach.created_at.desc())
        stmt = stmt.offset(max(page - 1, 0) * page_size).limit(page_size)
        items = list((await self.session.execute(stmt)).scalars().all())
        return items, total

    async def add(self, outreach: Outreach) -> Outreach:
        self.session.add(outreach)
        await self.session.flush()
        return outreach
