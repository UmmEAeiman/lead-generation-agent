"""Authentication service: registration and credential verification."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError, UnauthorizedError
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.users = UserRepository(session)
        self.session = session

    async def register(self, data: RegisterRequest) -> User:
        email = data.email.lower()
        existing = await self.users.get_by_email(email)
        if existing is not None:
            raise ConflictError("EMAIL_TAKEN", "An account with this email already exists.")
        user = User(
            email=email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
        )
        await self.users.add(user)
        await self.session.commit()
        return user

    async def authenticate(self, data: LoginRequest) -> User:
        email = data.email.lower()
        user = await self.users.get_by_email(email)
        if user is None or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedError("INVALID_CREDENTIALS", "Invalid email or password.")
        if not user.is_active:
            raise UnauthorizedError("ACCOUNT_DISABLED", "This account is disabled.")
        return user
