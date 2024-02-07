"""
This module provides API dependencies that can be utilized across
 multiple routes and modules.
It includes authentication utilities, connection handlers for external
 services like Redis, and factory functions for service classes.
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated, Any

from fastapi import Depends
from redis.asyncio import Redis

from app.api.redis_deps import RedisDependency
from app.config.db.auth_settings import AuthSettings

logger: logging.Logger = logging.getLogger(__name__)


class RedisConnectionManager:
    """
    Redis connection manager class
    """

    def __init__(self, auth_settings: AuthSettings):
        self.url: str = f"{auth_settings.REDIS_DATABASE_URI}"
        self.pool: Redis | None = None  # type: ignore

    async def start(self) -> None:
        """
        Start the redis pool connection
        :return: None
        :rtype: NoneType
        """
        self.pool = Redis.from_url(self.url, decode_responses=True)
        await self.pool.ping()
        logger.info("Redis Database initialized")

    async def stop(self) -> None:
        """
        Stops the redis connection
        :return: None
        :rtype: NoneType
        """
        await self.pool.close()  # type: ignore

    async def get_connection(self) -> Redis | None:  # type: ignore
        """
        Get the connection
        :return: The redis connection
        :rtype: Optional[Redis]
        """
        return self.pool

    @asynccontextmanager
    async def connection(self) -> AsyncGenerator[Redis, Any]:  # type: ignore
        """
        Asynchronously get the connection from the pool context manager
        :return: Yields the generator object
        :rtype: AsyncGenerator[Redis, Any]
        """
        await self.start()
        yield self.pool  # type: ignore
        await self.stop()


async def get_redis_dep(
    redis_dependency: Annotated[RedisDependency, Depends()],
) -> AsyncGenerator[Redis, None]:  # type: ignore
    """
    Lazy generation of Redis dependency
    :param redis_dependency: The dependency injection on Redis
    :type redis_dependency: RedisDependency
    :return: The Redis connection instance as a generator
    :rtype: AsyncGenerator[Redis, None]
    """
    async with redis_dependency as redis:
        yield redis
