from fastapi import APIRouter

from app.core.dependencies import CurrentUserDep
from app.schemas.auth import UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def me(user: CurrentUserDep) -> UserOut:
    return UserOut.model_validate(user)
