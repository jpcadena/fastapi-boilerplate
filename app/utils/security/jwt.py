"""
A module for jwt in the app.utils.security package.
"""
import logging
import time
from typing import Annotated, Any

from authlib.jose import JoseError, JWTClaims, jwt
from authlib.jose.errors import BadSignatureError, ExpiredTokenError
from fastapi import Depends, HTTPException, status

from app.config.config import get_auth_settings, get_init_settings
from app.config.db.auth_settings import AuthSettings
from app.config.init_settings import InitSettings

logger: logging.Logger = logging.getLogger(__name__)


def encode_jwt(
    payload: dict[str, Any],
    auth_settings: Annotated[AuthSettings, Depends(get_auth_settings)],
    init_settings: Annotated[InitSettings, Depends(get_init_settings)],
) -> str:
    """
    Encode a JSON Web Token (JWT) with the given payload.
    :param payload: The payload to encode
    :type payload: dict[str, Any]
    :param auth_settings: Dependency method for cached setting object
    :type auth_settings: AuthSettings
    :param init_settings: Dependency method for cached init setting object
    :type init_settings: InitSettings
    :return: The JSON Web Token
    :rtype: str
    """
    header: dict[str, str] = {'alg': auth_settings.ALGORITHM}
    try:
        encoded_jwt: bytes = jwt.encode(
            header, payload, auth_settings.SECRET_KEY
        )
        return encoded_jwt.decode(init_settings.ENCODING)
    except JoseError as exc:
        logger.error(f"Error encoding JWT: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error encoding JWT",
        ) from exc


def decode_jwt(
    token: str,
    auth_settings: Annotated[AuthSettings, Depends(get_auth_settings)],
) -> dict[str, Any]:
    """
    Validate the provided JWT token.
    :param token: JWT token to be validated
    :type token: str
    :param auth_settings: Dependency method for cached setting object
    :type auth_settings: AuthSettings
    :return: Decoded payload of the valid JWT token
    :rtype: dict[str, Any]
    """
    try:
        jwt_claims: JWTClaims = decode_and_validate_jwt(auth_settings, token)
        return dict(jwt_claims)
    except ExpiredTokenError as ete:
        logger.error(ete)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers=auth_settings.HEADERS,
        ) from ete
    except BadSignatureError as bse:
        logger.error(bse)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature",
            headers=auth_settings.HEADERS,
        ) from bse
    except JoseError as exc:
        logger.error(exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JWT token",
            headers=auth_settings.HEADERS,
        ) from exc


def decode_and_validate_jwt(
    auth_settings: Annotated[AuthSettings, Depends(get_auth_settings)],
    token: str,
) -> JWTClaims:
    """
    Decode a JWT token and validate its claims.
    :param auth_settings: Dependency method for cached setting object,
     containing authentication parameters like secret key, issuer URL, etc.
    :type auth_settings: AuthSettings
    :param token: The JWT token to be decoded and validated.
    :type token: str
    :return: A `JWTClaims` object representing the validated claims of the JWT.
    :rtype: JWTClaims
    """
    try:
        claims_options: dict[str, Any] = {
            'iss': {'essential': True, 'value': str(auth_settings.SERVER_URL)},
            'aud': {'essential': True, 'value': str(auth_settings.AUDIENCE)},
            'sub': {
                'essential': True,
            },
            'jti': {'essential': True},
        }
        decoded: JWTClaims = jwt.decode(
            token, auth_settings.SECRET_KEY, claims_options=claims_options
        )
        now: int = int(time.time())
        leeway: int = 60
        decoded.validate(now=now, leeway=leeway)
    except JoseError as exc:
        logger.error(exc)
        raise
    return decoded
