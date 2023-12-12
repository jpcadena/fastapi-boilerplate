"""
A module for rate limiter in the app.middlewares package.
"""
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
            if await rate_limiter_service.is_rate_limited(rate_limiter):
                await blacklist_service.add_to_blacklist(client_ip)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests",
                    headers={
                        "Retry-After": f"{auth_setting.RATE_LIMIT_DURATION}"
                    },
                )
        await self.app(scope, receive, send)
