from uuid import UUID

from fastapi import APIRouter, Query, status

from app.core.dependencies import CurrentUserDep, SessionDep
from app.schemas.common import Page
from app.schemas.lead import LeadCreate, LeadOut, LeadUpdate
from app.services.lead_service import LeadService
from app.services.outreach_service import OutreachService

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("", response_model=Page[LeadOut])
async def list_leads(
    session: SessionDep,
    user: CurrentUserDep,
    q: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    industry: str | None = None,
    location: str | None = None,
    score_min: int | None = None,
    score_max: int | None = None,
    sort: str = "created_at",
    order: str = "desc",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> Page[LeadOut]:
    items, total = await LeadService(session).list(
        user.id,
        q=q,
        status=status_filter,
        industry=industry,
        location=location,
        score_min=score_min,
        score_max=score_max,
        sort=sort,
        order=order,
        page=page,
        page_size=page_size,
    )
    return Page[LeadOut](
        items=[LeadOut.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/search", response_model=list[LeadOut])
async def similar_leads(
    session: SessionDep,
    user: CurrentUserDep,
    q: str = Query(min_length=1),
    limit: int = Query(default=10, ge=1, le=50),
) -> list[LeadOut]:
    leads = await LeadService(session).similar(user.id, q, limit=limit)
    return [LeadOut.model_validate(lead) for lead in leads]


@router.post("", response_model=LeadOut, status_code=status.HTTP_201_CREATED)
async def create_lead(data: LeadCreate, session: SessionDep, user: CurrentUserDep) -> LeadOut:
    lead = await LeadService(session).create(user.id, data)
    return LeadOut.model_validate(lead)


@router.get("/{lead_id}", response_model=LeadOut)
async def get_lead(lead_id: UUID, session: SessionDep, user: CurrentUserDep) -> LeadOut:
    lead = await LeadService(session).get(user.id, lead_id)
    return LeadOut.model_validate(lead)


@router.patch("/{lead_id}", response_model=LeadOut)
async def update_lead(
    lead_id: UUID, data: LeadUpdate, session: SessionDep, user: CurrentUserDep
) -> LeadOut:
    lead = await LeadService(session).update(user.id, lead_id, data)
    return LeadOut.model_validate(lead)


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(lead_id: UUID, session: SessionDep, user: CurrentUserDep) -> None:
    await LeadService(session).delete(user.id, lead_id)


@router.post("/{lead_id}/opt-out", status_code=status.HTTP_204_NO_CONTENT)
async def opt_out_lead(lead_id: UUID, session: SessionDep, user: CurrentUserDep) -> None:
    await OutreachService(session).opt_out(user.id, lead_id)
