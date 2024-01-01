"""
A module for ip blacklist in the app.services.infrastructure package.
"""

import logging
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends
from pydantic import IPvAnyAddress
from redis.asyncio import Redis

from app.api.deps import get_redis_dep
from app.config.config import auth_setting
from app.core.decorators import benchmark, with_logging
from app.db.auth import handle_redis_exceptions

logger: logging.Logger = logging.getLogger(__name__)


class IPBlacklistService:
    """
    Service class for IP blacklisting operations using Redis.
    """

    def __init__(self, redis: Redis):  # type: ignore
        self._redis: Redis = redis  # type: ignore

    @handle_redis_exceptions
    @with_logging
    @benchmark
    async def is_ip_blacklisted(self, ip: IPvAnyAddress) -> bool:
        """
        Check if the IP address is currently blacklisted.
        :param ip: The IP address to check.
        :type ip: IPvAnyAddress
        :return: True if blacklisted, False otherwise.
        :rtype: bool
        """
        return bool(await self._redis.get(self.get_redis_key(ip)))

    @handle_redis_exceptions
    @with_logging
    @benchmark
    async def blacklist_ip(self, ip: IPvAnyAddress) -> None:
        """
        Add the IP address to the blacklist.
        :param ip: The IP address to blacklist.
        :type ip: IPvAnyAddress
        :return: None
        :rtype: NoneType
        """
        await self._redis.setex(
            self.get_redis_key(ip),
            auth_setting.BLACKLIST_EXPIRATION_SECONDS,
            f"Blacklisted at {datetime.now(timezone.utc).isoformat()}",
        )

    @staticmethod
    def get_redis_key(ip: IPvAnyAddress) -> str:
        """
        Generate the Redis key for the given IP address.
        :param ip: The IP address.
        :type ip: IPvAnyAddress
        :return: The Redis key.
        :rtype: str
        """
        return f"blacklist:{ip}"


def get_ip_blacklist_service(
    redis: Annotated[Redis, Depends(get_redis_dep)]  # type: ignore
) -> IPBlacklistService:
    """
    Get an instance of the IP Blacklist service
    :param redis: Dependency method for async Redis connection
    :type redis: Redis
    :return: IPBlacklistService instance
    :rtype: IPBlacklistService
    """
    return IPBlacklistService(redis)
