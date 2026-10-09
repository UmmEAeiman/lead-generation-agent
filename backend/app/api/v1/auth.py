from fastapi import APIRouter, Response, status

from app.core.config import settings
from app.core.dependencies import SessionDep
from app.schemas.auth import LoginRequest, RegisterRequest, UserOut
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, session: SessionDep) -> UserOut:
    user = await AuthService(session).register(data)
    return UserOut.model_validate(user)


@router.post("/login", response_model=UserOut)
async def login(data: LoginRequest, response: Response, session: SessionDep) -> UserOut:
    user = await AuthService(session).authenticate(data)
    from app.core.security import create_access_token

    token = create_access_token(str(user.id))
    response.set_cookie(
        key=settings.cookie_name,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.access_token_expire_minutes * 60,
    )
    return UserOut.model_validate(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> Response:
    response.delete_cookie(settings.cookie_name)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
