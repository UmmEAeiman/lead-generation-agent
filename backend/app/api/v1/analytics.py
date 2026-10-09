from fastapi import APIRouter

from app.core.dependencies import CurrentUserDep, SessionDep
from app.schemas.analytics import AnalyticsOverview
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview", response_model=AnalyticsOverview)
async def overview(session: SessionDep, user: CurrentUserDep) -> AnalyticsOverview:
    return await AnalyticsService(session).overview(user.id)
