"""
A module for blacklist token in the app.middlewares package.
"""
import logging
from typing import Optional

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import RequestResponseEndpoint

from app.config.config import auth_setting
from app.services.infrastructure.token import TokenService

logger: logging.Logger = logging.getLogger(__name__)
SKIP_ROUTES: list[str] = [
    "/api/v1/auth/login",
    "/api/v1/auth/logout",
    "/api/v1/auth/recover-password",
    "/api/v1/auth/reset-password",
    "/api/v1/user",
]


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
    try:
        # Skip middleware for login route
        if not any(request.url.path.startswith(route) for route in SKIP_ROUTES):
            logger.info("Start of blacklist_middleware")
            auth_header: Optional[str] = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.replace("Bearer ", "", 1)
                token_service = TokenService(
                    request.app.state.redis_connection, auth_setting
                )
                is_blacklisted = await token_service.is_token_blacklisted(token)
                if is_blacklisted:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="This token has been blacklisted.",
                    )
            else:
                logger.info("No Bearer token found in request.")
            logger.info("End of blacklist_middleware")
    except HTTPException as e:
        logger.error(
            f"An HTTPException occurred: status_code={e.status_code},"
            f" detail={e.detail}"
        )
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise
    response: Response = await call_next(request)
    return response
