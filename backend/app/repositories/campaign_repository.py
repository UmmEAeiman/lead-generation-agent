from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign import Campaign


class CampaignRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, campaign_id: UUID, owner_id: UUID) -> Campaign | None:
        result = await self.session.execute(
            select(Campaign).where(Campaign.id == campaign_id, Campaign.owner_id == owner_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self, owner_id: UUID, *, page: int = 1, page_size: int = 20
    ) -> tuple[list[Campaign], int]:
        stmt = select(Campaign).where(Campaign.owner_id == owner_id)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = int((await self.session.execute(count_stmt)).scalar_one())
        stmt = stmt.order_by(Campaign.created_at.desc())
        stmt = stmt.offset(max(page - 1, 0) * page_size).limit(page_size)
        items = list((await self.session.execute(stmt)).scalars().all())
        return items, total

    async def add(self, campaign: Campaign) -> Campaign:
        self.session.add(campaign)
        await self.session.flush()
        return campaign
