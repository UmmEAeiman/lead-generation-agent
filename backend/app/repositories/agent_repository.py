from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent_run import AgentRun


class AgentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, run_id: str) -> AgentRun | None:
        return await self.session.get(AgentRun, run_id)

    async def list(
        self,
        user_id: str | None = None,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[AgentRun], int]:
        stmt = select(AgentRun)
        if user_id:
            stmt = stmt.where(AgentRun.user_id == user_id)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = int((await self.session.execute(count_stmt)).scalar_one())
        stmt = stmt.order_by(AgentRun.created_at.desc())
        stmt = stmt.offset(max(page - 1, 0) * page_size).limit(page_size)
        items = list((await self.session.execute(stmt)).scalars().all())
        return items, total

    async def add(self, run: AgentRun) -> AgentRun:
        self.session.add(run)
        await self.session.flush()
        return run

    async def update(self, run: AgentRun, fields: dict[str, Any]) -> AgentRun:
        for key, value in fields.items():
            if hasattr(run, key):
                setattr(run, key, value)
        await self.session.flush()
        return run
