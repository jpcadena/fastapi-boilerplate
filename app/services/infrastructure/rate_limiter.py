"""
A module for rate limiter in the app.services.infrastructure package.
"""
from datetime import datetime, timedelta

from pydantic import PositiveInt
from redis.asyncio import Redis

from app.config.config import auth_setting
from app.core.decorators import benchmark, with_logging
from app.db.auth import handle_redis_exceptions
from app.schemas.external.rate_limiter import RateLimiter


class RateLimiterService:
    """
    Service class for rate-limiting operations using Redis.
    """

    def __init__(
        self,
        redis: Redis,  # type: ignore
        rate_limit_duration: PositiveInt = auth_setting.RATE_LIMIT_DURATION,
        max_requests: PositiveInt = auth_setting.MAX_REQUESTS,
    ):
        self._redis: Redis = redis  # type: ignore
        self._rate_limit_duration: PositiveInt = rate_limit_duration
        self._max_requests: PositiveInt = max_requests

    @staticmethod
    def get_rate_limit_key(rate_limiter: RateLimiter) -> str:
        """
        Returns the rate limit key
        :param rate_limiter: The rate limiter instance
        :type rate_limiter: RateLimiter
        :return: The key to store on Redis based on the model instance
        :rtype: str
        """
        return (
            f"ratelimit:{str(rate_limiter.ip_address)}"
            f":{rate_limiter.user_agent}"
            f":{rate_limiter.request_path}"
        )

    @handle_redis_exceptions
    @with_logging
    @benchmark
    async def is_rate_limited(self, rate_limiter: RateLimiter) -> bool:
        """
        Check and update the rate limit for the given IP and request path.
        :param rate_limiter: The rate limiter instance
        :type rate_limiter: RateLimiter
        :return: True if the request exceeds the rate limit; otherwise false.
        :rtype: bool
        """
        rate_limit_key: str = self.get_rate_limit_key(rate_limiter)
        min_timestamp: datetime = datetime.now() - timedelta(
            seconds=self._rate_limit_duration
        )
        await self._redis.zremrangebyscore(
            rate_limit_key, "-inf", min_timestamp.timestamp()
        )
        now_timestamp: float = datetime.now().timestamp()
        await self._redis.zadd(rate_limit_key, {"now_timestamp": now_timestamp})
        request_count: int = await self._redis.zcard(rate_limit_key)
        return request_count > self._max_requests
