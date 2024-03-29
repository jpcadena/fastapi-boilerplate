"""
A module for password in the app.utils.security package.
"""

import logging
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

from fastapi import Depends
from pydantic import EmailStr

from app.config.config import get_auth_settings, get_init_settings
from app.config.db.auth_settings import AuthSettings
from app.config.init_settings import InitSettings
from app.utils.security.jwt import decode_jwt, encode_jwt

logger: logging.Logger = logging.getLogger(__name__)


def generate_password_reset_payload(
    email: EmailStr,
    auth_settings: Annotated[AuthSettings, Depends(get_auth_settings)],
) -> dict[str, Any]:
    """
    Generate a password reset payload
    :param email: The email to generate the reset token for
    :type email: EmailStr
    :param auth_settings: Dependency method for cached setting object
    :type auth_settings: AuthSettings
    :return: The payload to be used
    :rtype: dict[str, Any]
    """
    now: datetime = datetime.now(UTC)
    expires: datetime = now + timedelta(
        hours=auth_settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS
    )
    exp: float = expires.timestamp()
    payload: dict[str, Any] = {
        "iss": f"{auth_settings.SERVER_URL}",
        "exp": exp,
        "nbf": now,
        "sub": email,
    }
    logger.info("Payload generated for password")
    return payload


def generate_password_reset_token(
    email: EmailStr,
    auth_settings: Annotated[AuthSettings, Depends(get_auth_settings)],
    init_settings: Annotated[InitSettings, Depends(get_init_settings)],
) -> str:
    """
    Generate a password reset token for the given email address.
    :param email: The email to generate the reset token for
    :type email: EmailStr
    :param auth_settings: Dependency method for cached setting object
    :type auth_settings: AuthSettings
    :param init_settings: Dependency method for cached init setting object
    :type init_settings: InitSettings
    :return: The password reset token
    :rtype: str
    """
    payload: dict[str, Any] = generate_password_reset_payload(
        email, auth_settings
    )
    return encode_jwt(payload, auth_settings, init_settings)


def verify_password_reset_token(
    token: str,
    auth_settings: Annotated[AuthSettings, Depends(get_auth_settings)],
) -> EmailStr | None:
    """
    Verify a password reset token and return the email address if valid.
    :param token: The JSON Web Token
    :type token: str
    :param auth_settings: Dependency method for cached setting object
    :type auth_settings: AuthSettings
    :return: The email address
    :rtype: EmailStr
    """
    decoded_token: dict[str, Any] | None = decode_jwt(token, auth_settings)
    return decoded_token.get("sub") if decoded_token else None
