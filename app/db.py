from __future__ import annotations
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from app.config import settings

engine = create_async_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=30,
    pool_pre_ping=True,
)

SessionMaker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def healthcheck() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
