
from fastapi import APIRouter, BackgroundTasks, Query, status

from app.core.dependencies import CurrentUserDep, SessionDep
from app.schemas.agent import AgentRunOut, AgentRunRequest, QueuedRun
from app.schemas.common import Page
from app.services.agent_service import AgentService
from app.services.campaign_service import CampaignService

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post(
    "/{agent_type}/run",
    response_model=QueuedRun,
    status_code=status.HTTP_202_ACCEPTED,
)
async def run_agent(
    agent_type: str,
    data: AgentRunRequest,
    background_tasks: BackgroundTasks,
    session: SessionDep,
    user: CurrentUserDep,
) -> QueuedRun:
    icp = data.icp or {}
    if data.campaign_id is not None:
        campaign = await CampaignService(session).get(user.id, data.campaign_id)
        icp = CampaignService.icp_from(campaign)

    service = AgentService(session)
    run = await service.queue(
        user_id=user.id,
        agent_type=agent_type,
        icp=icp,
        lead_ids=data.lead_ids,
        campaign_id=data.campaign_id,
    )
    service.schedule(background_tasks, run.run_id)
    return QueuedRun(run_id=run.run_id, status=run.status)


@router.get("/runs", response_model=Page[AgentRunOut])
async def list_runs(
    session: SessionDep,
    user: CurrentUserDep,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> Page[AgentRunOut]:
    items, total = await AgentService(session).list(user.id, page=page, page_size=page_size)
    return Page[AgentRunOut](
        items=[AgentRunOut.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/runs/{run_id}", response_model=AgentRunOut)
async def get_run(run_id: str, session: SessionDep, user: CurrentUserDep) -> AgentRunOut:
    run = await AgentService(session).get(run_id, user.id)
    return AgentRunOut.model_validate(run)
