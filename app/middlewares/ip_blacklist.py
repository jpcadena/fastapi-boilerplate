"""
A module for ip blacklisting in the app.middlewares package.
"""
from ipaddress import AddressValueError, ip_address
from typing import Any, Callable, Optional

from fastapi import FastAPI, HTTPException, Request, status
from starlette.datastructures import Address

from app.exceptions.exceptions import NotFoundException
from app.services.infrastructure.ip_blacklist import IPBlacklistService


class BlacklistMiddleware:
    """
    Blacklist middleware for blocking blacklisted IPs.
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
            blacklist_service: IPBlacklistService = IPBlacklistService(
                request.app.state.redis_connection
            )
            client: Optional[Address] = request.client
            if not client:
                raise NotFoundException("No client available from request")
            try:
                client_ip = ip_address(client.host)
            except AddressValueError as e:
                raise NotFoundException("Invalid IP address") from e
            if await blacklist_service.is_ip_blacklisted(client_ip):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="IP address blacklisted due to excessive"
                    " violations.",
                )
        await self.app(scope, receive, send)
