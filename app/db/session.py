"""
Database session script
"""
import logging

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)

from app.config.config import sql_database_setting
from app.core.decorators import benchmark, with_logging

logger: logging.Logger = logging.getLogger(__name__)
url: str = sql_database_setting.SQLALCHEMY_DATABASE_URI.__str__()
async_engine: AsyncEngine = create_async_engine(
    url, pool_pre_ping=True, future=True, echo=True
)


@with_logging
@benchmark
async def get_session() -> AsyncSession:
    """
    Get an asynchronous session to the database
    :return session: Async session for database connection
    :rtype session: AsyncSession
    """
    async with AsyncSession(
        bind=async_engine, expire_on_commit=False
    ) as session:
        return session
