"""
A module for security headers in the app.middlewares package.
"""

from fastapi import Request, Response
from pydantic import PositiveInt
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding security headers to the response.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Dispatch the request with the security headers added to the response
        :param request: The HTTP request to be dispatched
        :type request: Request
        :param call_next: The call_next middleware function
        :type call_next: RequestResponseEndpoint
        :return: The response with the security headers added
        :rtype: Response
        """
        response: Response = await call_next(request)
        self._add_security_headers(
            response,
            request.app.state.auth_settings.STRICT_TRANSPORT_SECURITY_MAX_AGE,
        )
        return response

    @staticmethod
    def _add_security_headers(response: Response, max_age: PositiveInt) -> None:
        """
        Adds security headers to the response.
        :param max_age: The maximum age for the strict transport security
        :type max_age: PositiveInt
        :param response: The FastAPI response instance
        :type response: Response
        :return: None
        :rtype: NoneType
        """
        response.headers["Strict-Transport-Security"] = (
            f"max-age={max_age}; includeSubDomains;"
            # f" preload"  # Uncomment when using HTTPS for HSTS protection
        )
        # TODO: Add Content Security Policies support
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(self 'https://maps.googleapis.com'),"
            "microphone=self, camera=self, fullscreen=self,"
            "accelerometer=self, gyroscope=self"
        )
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["X-DNS-Prefetch-Control"] = "off"
        response.headers["X-Download-Options"] = "noopen"
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
