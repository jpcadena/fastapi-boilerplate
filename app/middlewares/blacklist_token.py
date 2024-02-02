"""
A module for blacklist token in the app.middlewares package.
"""

import logging

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import RequestResponseEndpoint

from app.services.infrastructure.token import TokenService

logger: logging.Logger = logging.getLogger(__name__)
SKIP_ROUTES: list[str] = [
    "/api/v1/auth/login",
    "/api/v1/auth/logout",
    "/api/v1/auth/recover-password",
    "/api/v1/auth/reset-password",
    "/api/v1/user",
    "/",
]


def extract_token(request: Request) -> str | None:
    """
    Extract token from the Authorization headers of the request
    :param request: The upcoming request instance
    :type request: Request
    :return: The token
    :rtype: Optional[str]
    """
    auth_header: str | None = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.replace("Bearer ", "", 1)
    return None


async def check_blacklist(token: str, request: Request) -> None:
    """
    Check if a token is blacklisted from the upcoming request
    :param token: The token to check
    :type token: str
    :param request: The upcoming request instance
    :type request: Request
    :return: None
    :rtype: NoneType
    """
    token_service: TokenService = TokenService(
        request.app.state.redis_connection,
        request.app.state.auth_settings,
    )
    if await token_service.is_token_blacklisted(token):
        logger.warning(f"Access attempt with blacklisted token: {token}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This token has been blacklisted.",
        )


async def process_request(request: Request) -> None:
    """
    Process request for the blacklist middleware
    :param request: The upcoming request instance
    :type request: Request
    :return: None
    :rtype: NoneType
    """
    token: str | None
    if token := extract_token(request):
        await check_blacklist(token, request)


async def blacklist_middleware(
    request: Request, call_next: RequestResponseEndpoint
) -> Response:
    """
    This middleware is used to blacklist access tokens for a given user
    :param request: The request object
    :type request: Request
    :param call_next: The next request function to call
    :type call_next: RequestResponseEndpoint
    :return: The response from the next call
    :rtype: Response
    """
    if not any(request.url.path.startswith(route) for route in SKIP_ROUTES):
        await process_request(request)
    response: Response = await call_next(request)
    return response
