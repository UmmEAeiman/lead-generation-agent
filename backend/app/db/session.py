"""Async engine and session factory (Neon Postgres in production, SQLite for dev)."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base import Base

_connect_args: dict = {}
_engine_kwargs: dict = {"echo": False}
if settings.is_sqlite:
    _connect_args = {"check_same_thread": False}
    _engine_kwargs = {"poolclass": StaticPool}

engine = create_async_engine(
    settings.database_url,
    connect_args=_connect_args,
    **_engine_kwargs,
)

SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
