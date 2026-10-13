from uuid import UUID

from fastapi import APIRouter, Query, status

from app.core.dependencies import CurrentUserDep, SessionDep
from app.schemas.common import Page
from app.schemas.outreach import OutreachOut, OutreachPrepareRequest
from app.services.outreach_service import OutreachService

router = APIRouter(prefix="/outreach", tags=["outreach"])


@router.get("", response_model=Page[OutreachOut])
async def list_outreach(
    session: SessionDep,
    user: CurrentUserDep,
    lead_id: UUID | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    run_id: str | None = None,
    campaign_id: UUID | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> Page[OutreachOut]:
    items, total = await OutreachService(session).list(
        user.id,
        lead_id=lead_id,
        status=status_filter,
        run_id=run_id,
        campaign_id=campaign_id,
        page=page,
        page_size=page_size,
    )
    return Page[OutreachOut](
        items=[OutreachOut.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/prepare", response_model=OutreachOut, status_code=status.HTTP_201_CREATED)
async def prepare_outreach(
    data: OutreachPrepareRequest, session: SessionDep, user: CurrentUserDep
) -> OutreachOut:
    outreach = await OutreachService(session).prepare(user.id, data)
    return OutreachOut.model_validate(outreach)


@router.post("/{outreach_id}/approve", response_model=OutreachOut)
async def approve_outreach(
    outreach_id: UUID, session: SessionDep, user: CurrentUserDep
) -> OutreachOut:
    outreach = await OutreachService(session).approve(user.id, outreach_id)
    return OutreachOut.model_validate(outreach)


@router.post("/{outreach_id}/send", response_model=OutreachOut)
async def send_outreach(
    outreach_id: UUID, session: SessionDep, user: CurrentUserDep
) -> OutreachOut:
    outreach = await OutreachService(session).send(user.id, outreach_id)
    return OutreachOut.model_validate(outreach)
