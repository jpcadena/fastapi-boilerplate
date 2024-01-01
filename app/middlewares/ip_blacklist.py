"""
A module for ip blacklisting in the app.middlewares package.
"""
from ipaddress import AddressValueError, IPv4Address, IPv6Address, ip_address
from typing import Any, Callable, Optional, Union

from fastapi import FastAPI, HTTPException, Request, status
from starlette.datastructures import Address

from app.exceptions.exceptions import NotFoundException
from app.services.infrastructure.ip_blacklist import IPBlacklistService


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
            # app: FastAPI = scope['app']
            ip_blacklist_service: IPBlacklistService = (
                request.app.state.ip_blacklist_service
            )
            client_ip: Union[IPv4Address, IPv6Address] = self.get_client_ip(
                request
            )
            if await self.is_blacklisted(ip_blacklist_service, client_ip):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: IP blacklisted.",
                )
        await self.app(scope, receive, send)

    @staticmethod
    def get_client_ip(request: Request) -> Union[IPv4Address, IPv6Address]:
        """
        Extract the client IP address from the request.
        :param request: The FastAPI request object.
        :type request: Request
        :return: The extracted IP address.
        :rtype: Union[IPv4Address, IPv6Address]
        """
        client: Optional[Address] = request.client
        if not client:
            raise NotFoundException("No client found on the request")
        client_ip: str = client.host
        try:
            return ip_address(client_ip)
        except AddressValueError as exc:
            raise ValueError("Invalid IP address in the request.") from exc

    @staticmethod
    async def is_blacklisted(
        ip_blacklist_service: IPBlacklistService,
        ip: Union[IPv4Address, IPv6Address],
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
