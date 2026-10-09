from uuid import UUID

from fastapi import APIRouter, Query, status

from app.core.dependencies import CurrentUserDep, SessionDep
from app.schemas.campaign import CampaignCreate, CampaignOut, CampaignUpdate
from app.schemas.common import Page
from app.services.campaign_service import CampaignService

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("", response_model=Page[CampaignOut])
async def list_campaigns(
    session: SessionDep,
    user: CurrentUserDep,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> Page[CampaignOut]:
    items, total = await CampaignService(session).list(user.id, page=page, page_size=page_size)
    return Page[CampaignOut](
        items=[CampaignOut.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=CampaignOut, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    data: CampaignCreate, session: SessionDep, user: CurrentUserDep
) -> CampaignOut:
    campaign = await CampaignService(session).create(user.id, data)
    return CampaignOut.model_validate(campaign)


@router.get("/{campaign_id}", response_model=CampaignOut)
async def get_campaign(
    campaign_id: UUID, session: SessionDep, user: CurrentUserDep
) -> CampaignOut:
    campaign = await CampaignService(session).get(user.id, campaign_id)
    return CampaignOut.model_validate(campaign)


@router.patch("/{campaign_id}", response_model=CampaignOut)
async def update_campaign(
    campaign_id: UUID, data: CampaignUpdate, session: SessionDep, user: CurrentUserDep
) -> CampaignOut:
    campaign = await CampaignService(session).update(user.id, campaign_id, data)
    return CampaignOut.model_validate(campaign)
