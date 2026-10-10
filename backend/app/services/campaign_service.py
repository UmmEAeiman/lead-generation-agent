"""Campaign business logic."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.models.campaign import Campaign
from app.repositories.campaign_repository import CampaignRepository
from app.schemas.campaign import CampaignCreate, CampaignUpdate


class CampaignService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = CampaignRepository(session)
        self.session = session

    async def create(self, owner_id: UUID, data: CampaignCreate) -> Campaign:
        campaign = Campaign(owner_id=owner_id, **data.model_dump())
        await self.repo.add(campaign)
        await self.session.commit()
        return campaign

    async def list(
        self, owner_id: UUID, page: int = 1, page_size: int = 20
    ) -> tuple[list[Campaign], int]:
        return await self.repo.list(owner_id, page=page, page_size=page_size)

    async def get(self, owner_id: UUID, campaign_id: UUID) -> Campaign:
        campaign = await self.repo.get_by_id(campaign_id, owner_id)
        if campaign is None:
            raise NotFoundError("CAMPAIGN_NOT_FOUND", "The requested campaign does not exist.")
        return campaign

    async def update(self, owner_id: UUID, campaign_id: UUID, data: CampaignUpdate) -> Campaign:
        campaign = await self.get(owner_id, campaign_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            if hasattr(campaign, key):
                setattr(campaign, key, value)
        await self.session.commit()
        return campaign

    @staticmethod
    def icp_from(campaign: Campaign) -> dict:
        return {
            "industry": campaign.target_industry,
            "location": campaign.target_location,
            "company_size": campaign.target_company_size,
            "keywords": list(campaign.keywords or []),
        }
