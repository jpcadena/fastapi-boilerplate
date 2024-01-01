"""
A module for rate limiter in the app.middlewares package.
"""
from datetime import datetime
from ipaddress import AddressValueError, ip_address
from typing import Any, Callable, Optional

from fastapi import FastAPI, HTTPException, Request, status
from pydantic import IPvAnyAddress
from starlette.datastructures import Address

from app.config.config import auth_setting
from app.exceptions.exceptions import NotFoundException
from app.schemas.external.rate_limiter import RateLimiter
from app.services.infrastructure.ip_blacklist import IPBlacklistService
from app.services.infrastructure.rate_limiter import RateLimiterService


class RateLimiterMiddleware:
    """
    Rate limiter middleware for rate limiting applications requests
    """

    def __init__(self, app: FastAPI):
        self.app: FastAPI = app

    async def __call__(
        self,
        scope: dict[str, Any],
        receive: Callable[..., Any],
        send: Callable[..., Any],
    ) -> None:
        if scope["type"] == "http":
            request: Request = Request(scope, receive=receive)
            rate_limiter_service: RateLimiterService = RateLimiterService(
                request.app.state.redis_connection
            )
            blacklist_service: IPBlacklistService = IPBlacklistService(
                request.app.state.redis_connection
            )
            client: Optional[Address] = request.client
            if not client:
                raise NotFoundException("No client found on the request")
            try:
                client_ip = ip_address(client.host)
            except AddressValueError as e:
                raise NotFoundException("Invalid IP address") from e
            user_agent: str = request.headers.get("user-agent", "unknown")
            request_path: str = request.url.path
            rate_limiter: RateLimiter = RateLimiter(
                ip_address=IPvAnyAddress(client_ip),
                user_agent=user_agent,
                request_path=request_path,
            )
            # Add the request and clean up old requests
            await rate_limiter_service.add_request(rate_limiter)
            # Check if the rate limit has been exceeded
            request_count: int = await rate_limiter_service.get_request_count(
                rate_limiter
            )
            remaining_requests: int = (
                await rate_limiter_service.get_remaining_requests(rate_limiter)
            )
            reset_time: datetime = await rate_limiter_service.get_reset_time(
                rate_limiter
            )
            if request_count > auth_setting.MAX_REQUESTS:
                await blacklist_service.blacklist_ip(client_ip)
                headers: dict[str, str] = {
                    "X-RateLimit-Limit": str(auth_setting.MAX_REQUESTS),
                    "X-RateLimit-Remaining": str(max(0, remaining_requests)),
                    "X-RateLimit-Reset": str(int(reset_time.timestamp())),
                }
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests",
                    headers=headers,
                )
        await self.app(scope, receive, send)
