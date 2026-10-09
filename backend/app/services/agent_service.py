"""Agent run orchestration service: queue runs and track their state."""

from uuid import UUID

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.orchestrator import Orchestrator
from app.core.config import settings
from app.core.errors import AppError, NotFoundError
from app.db.session import SessionLocal
from app.models.agent_run import AgentRun
from app.models.enums import AgentRunStatus, AgentType
from app.repositories.agent_repository import AgentRepository
from app.utils.helpers import new_run_id

SINGLE_AGENT_TYPES = {
    AgentType.DISCOVERY.value,
    AgentType.ENRICHMENT.value,
    AgentType.RESEARCH.value,
    AgentType.QUALIFICATION.value,
    AgentType.PERSONALIZATION.value,
    AgentType.FOLLOWUP.value,
}
# Discovery produces leads, so it never starts from existing lead_ids.
LEAD_REQUIRED_TYPES = SINGLE_AGENT_TYPES - {AgentType.DISCOVERY.value}
VALID_AGENT_TYPES = SINGLE_AGENT_TYPES | {AgentType.PIPELINE.value}


async def execute_run(run_id: str) -> None:
    """Background entry point: runs outside the request cycle with its own session."""
    async with SessionLocal() as session:
        await Orchestrator(session).execute(run_id)


class AgentService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = AgentRepository(session)
        self.session = session

    async def queue(
        self,
        *,
        user_id: UUID,
        agent_type: str,
        icp: dict | None = None,
        lead_ids: list[UUID] | None = None,
        campaign_id: UUID | None = None,
    ) -> AgentRun:
        if agent_type not in VALID_AGENT_TYPES:
            raise AppError("UNKNOWN_AGENT", f"Unknown agent type '{agent_type}'.", 400)
        lead_ids = lead_ids or []
        if agent_type in LEAD_REQUIRED_TYPES and not lead_ids:
            raise AppError(
                "LEAD_IDS_REQUIRED",
                f"Agent '{agent_type}' requires at least one lead_id.",
                422,
            )
        run = AgentRun(
            run_id=new_run_id(),
            agent_type=agent_type,
            user_id=str(user_id),
            campaign_id=str(campaign_id) if campaign_id else None,
            status=AgentRunStatus.QUEUED.value,
            input_summary={
                "lead_ids": [str(i) for i in lead_ids],
                "icp": icp or {},
                "campaign_id": str(campaign_id) if campaign_id else None,
            },
        )
        await self.repo.add(run)
        await self.session.commit()
        return run

    def schedule(self, background_tasks: BackgroundTasks, run_id: str) -> None:
        background_tasks.add_task(execute_run, run_id)

    async def get(self, run_id: str, user_id: UUID) -> AgentRun:
        run = await self.repo.get(run_id)
        if run is None or run.user_id != str(user_id):
            raise NotFoundError("RUN_NOT_FOUND", "The requested agent run does not exist.")
        return run

    async def list(
        self, user_id: UUID, *, page: int = 1, page_size: int | None = None
    ) -> tuple[list[AgentRun], int]:
        size = page_size or settings.page_size_default
        return await self.repo.list(str(user_id), page=page, page_size=size)
