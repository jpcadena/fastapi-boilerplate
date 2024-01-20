"""
A module for ip blacklist in the app.services.infrastructure package.
"""
import logging
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends
from pydantic import IPvAnyAddress, PositiveInt
from redis.asyncio import Redis

from app.api.deps import get_redis_dep
from app.config.config import get_auth_settings
from app.config.db.auth_settings import AuthSettings
from app.db.auth import handle_redis_exceptions

logger: logging.Logger = logging.getLogger(__name__)


class IPBlacklistService:
    """
    Service class for IP blacklisting operations using Redis.
    """

    def __init__(
        self,
        redis: Redis,  # type: ignore
        blacklist_expiration_seconds: PositiveInt,
    ):
        self._redis: Redis = redis  # type: ignore
        self._expiration_seconds: PositiveInt = blacklist_expiration_seconds

    @handle_redis_exceptions
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
            self._expiration_seconds,
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
    redis: Annotated[Redis, Depends(get_redis_dep)],  # type: ignore
    auth_settings: Annotated[AuthSettings, Depends(get_auth_settings)],
) -> IPBlacklistService:
    """
    Get an instance of the IP Blacklist service
    :param redis: Dependency method for async Redis connection
    :type redis: Redis
    :param auth_settings: Dependency method for cached setting object
    :type auth_settings: AuthSettings
    :return: IPBlacklistService instance
    :rtype: IPBlacklistService
    """
    return IPBlacklistService(redis, auth_settings.BLACKLIST_EXPIRATION_SECONDS)
