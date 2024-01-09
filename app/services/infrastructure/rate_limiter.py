"""
A module for rate limiter in the app.services.infrastructure package.
"""
from datetime import datetime, timedelta
from typing import Any

from pydantic import PositiveInt
from redis.asyncio import Redis

from app.db.auth import handle_redis_exceptions
from app.schemas.external.rate_limiter import RateLimiter


class RateLimiterService:
    """
    Service class for rate-limiting operations using Redis.
    """

    def __init__(
        self,
        redis: Redis,  # type: ignore
        rate_limit_duration: PositiveInt,
        max_requests: PositiveInt,
        rate_limiter: RateLimiter,
    ):
        self._redis: Redis = redis  # type: ignore
        self._rate_limit_duration: PositiveInt = rate_limit_duration
        self._max_requests: PositiveInt = max_requests
        self._rate_limiter: RateLimiter = rate_limiter

    def get_rate_limit_key(self) -> str:
        """
        Returns the rate limit key
        :return: The key to store on Redis based on the model instance
        :rtype: str
        """
        return (
            f"ratelimit:{str(self._rate_limiter.ip_address)}"
            f":{self._rate_limiter.user_agent}"
            f":{self._rate_limiter.request_path}"
        )

    @handle_redis_exceptions
    async def add_request(self) -> None:
        """
        Add a new request and clean up old requests.
        :return: None
        :rtype: NoneType
        """
        rate_limit_key: str = self.get_rate_limit_key()
        min_timestamp: datetime = datetime.now() - timedelta(
            seconds=self._rate_limit_duration
        )
        now_timestamp: float = datetime.now().timestamp()
        await self._redis.zremrangebyscore(
            rate_limit_key, "-inf", min_timestamp.timestamp()
        )
        await self._redis.zadd(
            rate_limit_key, {f"{now_timestamp}": now_timestamp}
        )

    @handle_redis_exceptions
    async def get_request_count(self) -> int:
        """
        Get the number of requests in the current window.
        :return: The number of requests in the current window
        :rtype: int
        """
        rate_limit_key: str = self.get_rate_limit_key()
        return await self._redis.zcard(rate_limit_key)

    async def get_remaining_requests(self) -> int:
        """
        Calculate the remaining requests.
        :return: The remaining requests available
        :rtype: int
        """
        request_count: int = await self.get_request_count()
        return self._max_requests - request_count

    @handle_redis_exceptions
    async def get_reset_time(self) -> datetime:
        """
        Calculate the reset time.
        :return: The reset time available
        :rtype: datetime
        """
        rate_limit_key: str = self.get_rate_limit_key()
        oldest_request: list[tuple[Any, float]] = await self._redis.zrange(
            rate_limit_key, 0, 0, withscores=True
        )
        oldest_timestamp: datetime = (
            datetime.fromtimestamp(oldest_request[0][1])
            if oldest_request
            else datetime.now()
        )
        return oldest_timestamp + timedelta(seconds=self._rate_limit_duration)
