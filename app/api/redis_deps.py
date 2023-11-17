"""
A module for redis deps in the app.api package.
"""
import logging
from typing import Any, Optional

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.config.config import auth_setting

logger: logging.Logger = logging.getLogger(__name__)


class RedisDependency:
    """
    A class to handle Redis connections as a FastAPI dependency.
    """

    def __init__(self) -> None:
        self._url: str = str(auth_setting.REDIS_DATABASE_URI)
        self._redis: Optional[Redis] = None  # type: ignore

    async def init_redis(self) -> None:
        """
        Initializes the redis connection
        :return: None
        :rtype: NoneType
        """
        try:
            self._redis = Redis.from_url(
                self._url,
                decode_responses=True,
            )
        except RedisError as exc:
            logger.error("Failed to establish Redis connection: %s", exc)
            raise

    async def close_redis(self) -> None:
        """
        Closes the redis connection
        :return: None
        :rtype: NoneType
        """
        try:
            if self._redis:
                await self._redis.close()
        except RedisError as exc:
            logger.error("Failed to close Redis connection: %s", exc)
            raise

    async def __aenter__(self) -> Redis:  # type: ignore
        await self.init_redis()
        if self._redis:
            return self._redis

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close_redis()
