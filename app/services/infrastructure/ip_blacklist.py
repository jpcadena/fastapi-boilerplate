"""
A module for ip blacklist in the app.services.infrastructure package.
"""
import logging
from datetime import datetime

from pydantic import IPvAnyAddress
from redis.asyncio import Redis

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
    async def is_ip_blacklisted(self, ip_address: IPvAnyAddress) -> bool:
        """
        Check if the given IP address is blacklisted
        :param ip_address: The IP address to check
        :type ip_address: IPvAnyAddress
        :return: True if the IP address is blacklisted; False otherwise
        :rtype: bool
        """
        blacklisted_reason = await self._redis.get(f"blacklist:{ip_address}")
        return bool(blacklisted_reason)

    @handle_redis_exceptions
    @with_logging
    @benchmark
    async def add_to_blacklist(self, ip_address: IPvAnyAddress) -> None:
        """
        Add a new IP address to the blacklist on Redis
        :param ip_address: The new IP address to add to the blacklist
        :type ip_address: IPvAnyAddress
        :return: None
        :rtype: NoneType
        """
        await self._redis.setex(
            f"blacklist:{ip_address}",
            auth_setting.BLACKLIST_EXPIRATION_SECONDS,
            f"Blacklisted at {datetime.utcnow()}"
            f" due to excessive rate limiting violations.",
        )
