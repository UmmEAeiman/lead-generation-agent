from typing import Any
from uuid import UUID

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.llm.embeddings import cosine_similarity
from app.models.lead import Lead

_SORTABLE = {
    "created_at": Lead.created_at,
    "lead_score": Lead.lead_score,
    "company_name": Lead.company_name,
    "updated_at": Lead.updated_at,
}


class LeadRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _owned(self, owner_id: UUID) -> Select:
        return select(Lead).where(Lead.owner_id == owner_id)

    async def get_by_id(self, lead_id: UUID, owner_id: UUID) -> Lead | None:
        result = await self.session.execute(
            self._owned(owner_id).where(Lead.id == lead_id)
        )
        return result.scalar_one_or_none()

    async def get_many(self, lead_ids: list[UUID], owner_id: UUID) -> list[Lead]:
        if not lead_ids:
            return []
        result = await self.session.execute(
            self._owned(owner_id).where(Lead.id.in_(lead_ids))
        )
        return list(result.scalars().all())

    def _filtered(
        self,
        owner_id: UUID,
        *,
        q: str | None = None,
        status: str | None = None,
        industry: str | None = None,
        location: str | None = None,
        score_min: int | None = None,
        score_max: int | None = None,
    ) -> Select:
        stmt = self._owned(owner_id)
        if q:
            pattern = f"%{q.strip()}%"
            stmt = stmt.where(
                or_(
                    Lead.company_name.ilike(pattern),
                    Lead.contact_name.ilike(pattern),
                    Lead.email.ilike(pattern),
                )
            )
        if status:
            stmt = stmt.where(Lead.status == status)
        if industry:
            stmt = stmt.where(Lead.industry.ilike(f"%{industry.strip()}%"))
        if location:
            stmt = stmt.where(Lead.location.ilike(f"%{location.strip()}%"))
        if score_min is not None:
            stmt = stmt.where(Lead.lead_score >= score_min)
        if score_max is not None:
            stmt = stmt.where(Lead.lead_score <= score_max)
        return stmt

    async def list(
        self,
        owner_id: UUID,
        *,
        q: str | None = None,
        status: str | None = None,
        industry: str | None = None,
        location: str | None = None,
        score_min: int | None = None,
        score_max: int | None = None,
        sort: str = "created_at",
        order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Lead], int]:
        stmt = self._filtered(
            owner_id,
            q=q,
            status=status,
            industry=industry,
            location=location,
            score_min=score_min,
            score_max=score_max,
        )
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = int((await self.session.execute(count_stmt)).scalar_one())

        column = _SORTABLE.get(sort, Lead.created_at)
        ordered = stmt.order_by(column.desc() if order.lower() == "desc" else column.asc())
        ordered = ordered.offset(max(page - 1, 0) * page_size).limit(page_size)
        items = list((await self.session.execute(ordered)).scalars().all())
        return items, total

    async def find_duplicate(
        self,
        owner_id: UUID,
        *,
        normalized_domain: str | None,
        normalized_email: str | None,
        exclude_id: UUID | None = None,
    ) -> Lead | None:
        stmt = self._owned(owner_id)
        conditions = []
        if normalized_domain:
            conditions.append(Lead.normalized_domain == normalized_domain)
        if normalized_email:
            conditions.append(Lead.normalized_email == normalized_email)
        if not conditions:
            return None
        stmt = stmt.where(or_(*conditions))
        if exclude_id:
            stmt = stmt.where(Lead.id != exclude_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def add(self, lead: Lead) -> Lead:
        self.session.add(lead)
        await self.session.flush()
        return lead

    async def apply(self, lead: Lead, fields: dict[str, Any]) -> Lead:
        for key, value in fields.items():
            if hasattr(lead, key):
                setattr(lead, key, value)
        await self.session.flush()
        return lead

    async def similar_leads(
        self, owner_id: UUID, embedding: list[float], limit: int = 10
    ) -> list[tuple[Lead, float]]:
        stmt = self._owned(owner_id)
        if self.session.bind is not None and self.session.bind.dialect.name == "postgresql":

            distance = Lead.embedding.l2_distance(embedding)
            result = await self.session.execute(
                stmt.order_by(distance).limit(limit)
            )
            return [(lead, float(index)) for index, lead in enumerate(result.scalars().all())]

        result = await self.session.execute(stmt.where(Lead.embedding.is_not(None)))
        scored = []
        for lead in result.scalars().all():
            vector = list(lead.embedding) if lead.embedding is not None else []
            scored.append((lead, -cosine_similarity(embedding, vector)))
        scored.sort(key=lambda item: item[1])
        return scored[:limit]
