"""
A module for ip blacklisting in the app.middlewares package.
"""

from collections.abc import Callable
from ipaddress import IPv4Address, IPv6Address
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status

from app.services.infrastructure.ip_blacklist import IPBlacklistService
from app.utils.utils import get_client_ip


class IPBlacklistMiddleware:
    """
    Middleware class representation for blocking blacklisted IPs.
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
            ip_blacklist_service: IPBlacklistService = (
                request.app.state.ip_blacklist_service
            )
            client_ip: IPv4Address | IPv6Address = get_client_ip(
                request, request.app.state.auth_settings
            )
            if await self.is_blacklisted(ip_blacklist_service, client_ip):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: IP blacklisted.",
                )
        await self.app(scope, receive, send)

    @staticmethod
    async def is_blacklisted(
        ip_blacklist_service: IPBlacklistService,
        ip: IPv4Address | IPv6Address,
    ) -> bool:
        """
        Check if the given IP address is blacklisted.
        :param ip_blacklist_service: IP Blacklist Service instance
        :type ip_blacklist_service: IPBlacklistService
        :param ip: The IP address to check.
        :type ip: Union[IPv4Address, IPv6Address]
        :return: True if blacklisted, False otherwise.
        :rtype: bool
        """
        blacklisted: bool = await ip_blacklist_service.is_ip_blacklisted(ip)
        return blacklisted
