"""
A module for security headers in the app.middlewares package.
"""
from fastapi import Request, Response
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)

from app.config.config import auth_setting


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
        self.add_security_headers(response)
        return response

    @staticmethod
    def add_security_headers(response: Response) -> None:
        """
        Adds security headers to the response.
        :param response: The FastAPI response instance
        :type response: Response
        :return: None
        :rtype: NoneType
        """
        response.headers["Strict-Transport-Security"] = (
            f"max-age={auth_setting.STRICT_TRANSPORT_SECURITY_MAX_AGE}; "
            f"includeSubDomains"
        )
        # TODO: Add Content Security Policies support
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
        response.headers["Permissions-Policy"] = (
            "geolocation=(self 'https://maps.googleapis.com'),"
            "microphone=self, camera=self, fullscreen=self,"
            "accelerometer=self, gyroscope=self"
        )
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["X-DNS-Prefetch-Control"] = "off"
