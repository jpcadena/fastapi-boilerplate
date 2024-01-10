"""
A module for rate limiter in the app.middlewares package.
"""
from datetime import datetime
from ipaddress import IPv4Address, IPv6Address
from typing import Any, Callable, Union

from fastapi import FastAPI, HTTPException, Request, status
from pydantic import IPvAnyAddress

from app.schemas.external.rate_limiter import RateLimiter
from app.services.infrastructure.rate_limiter import RateLimiterService
from app.utils.utils import get_client_ip


class RateLimiterMiddleware:
    """
    Rate limiter middleware for rate limiting applications requests
    """

    def __init__(self, app: FastAPI):
        self.app: FastAPI = app

    @staticmethod
    async def handle_rate_limit_exceeded(
        rate_limiter: RateLimiter,
        rate_limiter_service: RateLimiterService,
        request: Request,
    ) -> None:
        """
        Handle rate limit exceeded for the given request
        :param rate_limiter: The rate limiter schema instance
        :type rate_limiter: RateLimiter
        :param rate_limiter_service: The Rate Limiter Service instance
        :type rate_limiter_service: RateLimiterService
        :param request: The request instance
        :type request: Request
        :return: None
        :rtype: NoneType
        """
        remaining_requests: int = (
            await rate_limiter_service.get_remaining_requests()
        )
        reset_time: datetime = await rate_limiter_service.get_reset_time()
        await request.app.state.ip_blacklist_service.blacklist_ip(
            rate_limiter.ip_address
        )
        headers: dict[str, str] = {
            "X-RateLimit-Limit": str(
                request.app.state.auth_settings.MAX_REQUESTS
            ),
            "X-RateLimit-Remaining": str(max(0, remaining_requests)),
            "X-RateLimit-Reset": str(int(reset_time.timestamp())),
            "Retry-After": str(
                int(reset_time.timestamp() - datetime.now().timestamp())
            ),
        }
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests",
            headers=headers,
        )

    async def enforce_rate_limit(
        self,
        rate_limiter: RateLimiter,
        rate_limiter_service: RateLimiterService,
        request: Request,
    ) -> None:
        """
        Enforce rate limit for a request
        :param rate_limiter: The rate limiter schema instance
        :type rate_limiter: RateLimiter
        :param rate_limiter_service: The Rate Limiter Service instance
        :type rate_limiter_service: RateLimiterService
        :param request: The request instance
        :type request: Request
        :return: None
        :rtype: NoneType
        """
        await rate_limiter_service.add_request()
        request_count: int = await rate_limiter_service.get_request_count()
        if request_count > request.app.state.auth_settings.MAX_REQUESTS:
            await self.handle_rate_limit_exceeded(
                rate_limiter, rate_limiter_service, request
            )

    async def process_request(self, request: Request) -> None:
        """
        Process a backend request from the middleware
        :param request: The upcoming request instance
        :type request: Request
        :return: None
        :rtype: NoneType
        """
        client_ip: Union[IPv4Address, IPv6Address] = get_client_ip(
            request, request.app.state.auth_settings
        )
        user_agent: str = request.headers.get("user-agent", "unknown")
        request_path: str = request.url.path
        rate_limiter: RateLimiter = RateLimiter(
            ip_address=IPvAnyAddress(client_ip),
            user_agent=user_agent,
            request_path=request_path,
        )
        rate_limiter_service: RateLimiterService = RateLimiterService(
            request.app.state.redis_connection,
            request.app.state.auth_settings.RATE_LIMIT_DURATION,
            request.app.state.auth_settings.MAX_REQUESTS,
            rate_limiter,
        )
        await self.enforce_rate_limit(
            rate_limiter, rate_limiter_service, request
        )

    async def __call__(
        self,
        scope: dict[str, Any],
        receive: Callable[..., Any],
        send: Callable[..., Any],
    ) -> None:
        if scope["type"] == "http":
            request = Request(scope, receive=receive)
            await self.process_request(request)
        await self.app(scope, receive, send)
