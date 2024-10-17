"""
Database session script
"""

import logging
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config.config import sql_database_setting
from app.core.decorators import benchmark, with_logging

logger: logging.Logger = logging.getLogger(__name__)
url: str = f"{sql_database_setting.SQLALCHEMY_DATABASE_URI}"
async_engine: AsyncEngine = create_async_engine(
    url, pool_pre_ping=True, future=True, echo=True
)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
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


async def get_session_generator() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an asynchronous session to the database as a generator

    :yield: Async session for database connection
    :rtype: AsyncGenerator[AsyncSession, None]
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error("Session rollback because of exception: %s", e)
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get the database session as a context manager from generator

    :return: The session generated
    :rtype: AsyncGenerator[AsyncSession, None]
    """
    async for session in get_session_generator():
        yield session


async def check_db_health(session: AsyncSession) -> bool:
    """
    Check the health of the database connection.

    :param session: The SQLAlchemy asynchronous session object used to
     interact with the database.
    :type session: AsyncSession
    :returns: True if the database connection is healthy, False otherwise.
    :rtype: bool
    """
    try:
        await session.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database connection error: {e}")
        return False
