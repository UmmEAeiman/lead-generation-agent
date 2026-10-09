"""Shared FastAPI dependencies: database session and authentication."""

from collections.abc import AsyncIterator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ForbiddenError, UnauthorizedError
from app.core.security import TokenError, decode_access_token
from app.db.session import SessionLocal
from app.models.user import User


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


def _extract_token(request: Request) -> str | None:
    token = request.cookies.get("access_token")
    if token:
        return token
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header.removeprefix("Bearer ").strip()
    return None


async def get_current_user(request: Request, session: SessionDep) -> User:
    token = _extract_token(request)
    if not token:
        raise UnauthorizedError()
    try:
        payload = decode_access_token(token)
    except TokenError as exc:
        raise UnauthorizedError(message="Invalid or expired session.") from exc
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError()
    try:
        user_uuid = UUID(str(user_id))
    except ValueError as exc:
        raise UnauthorizedError(message="Invalid session subject.") from exc
    from app.repositories.user_repository import UserRepository

    user = await UserRepository(session).get_by_id(user_uuid)
    if user is None or not user.is_active:
        raise ForbiddenError(message="Account is unavailable.")
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
