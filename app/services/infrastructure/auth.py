"""
A module for auth in the app.services package.
"""
import logging
import time
from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from redis.asyncio import Redis

from app.config.config import get_auth_settings
from app.config.db.auth_settings import AuthSettings
from app.core.security.jwt import create_access_token, create_refresh_token
from app.models.sql.user import User
from app.models.unstructured.token import Token as TokenDB
from app.schemas.external.token import Token, TokenPayload, TokenResponse
from app.services.infrastructure.token import TokenService
from app.utils.utils import get_nationality_code

logger: logging.Logger = logging.getLogger(__name__)


class AuthService:
    """
    Service class for user authentication.
    """

    @staticmethod
    def _build_payload(
        user: User,
        auth_settings: Annotated[AuthSettings, Depends(get_auth_settings)],
    ) -> TokenPayload:
        """
        Build JWT payload for authentication
        :param user: User to authenticate
        :type user: User
        :param auth_settings: Dependency method for cached setting object
        :type auth_settings: AuthSettings
        :return: Payload for JWT
        :rtype: TokenPayload
        """
        current_time: int = int(time.time())
        expiration_time: int = current_time + int(
            auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        user_data: dict[str, Any] = {
            "sub": f"username:{str(user.id)}",
            "nationalities": [get_nationality_code(user.address.country)],
            "email": user.email,
            "nickname": user.username,
            "preferred_username": user.username,
            "given_name": user.first_name,
            "family_name": user.last_name,
            "middle_name": user.middle_name,
            "gender": user.gender,
            "birthdate": user.birthdate,
            "updated_at": user.updated_at,
            "phone_number": user.phone_number,
            "address": user.address,
            "exp": expiration_time,
            "nbf": current_time - 1,
            "iat": current_time,
        }
        return TokenPayload(**user_data)

    @staticmethod
    def auth_token(
        user: User,
        auth_settings: Annotated[AuthSettings, Depends(get_auth_settings)],
    ) -> Token:
        """
        Authenticate a user and generate access and refresh tokens
        :param user: User to authenticate
        :type user: User
        :param auth_settings: Dependency method for cached setting object
        :type auth_settings: AuthSettings
        :return: Token object with access and refresh tokens
        :rtype: Token
        """
        payload: TokenPayload = AuthService._build_payload(user, auth_settings)
        access_token: str = create_access_token(
            payload=payload, auth_settings=auth_settings
        )
        refresh_token: str = create_refresh_token(
            payload=payload, auth_settings=auth_settings
        )
        return Token(access_token=access_token, refresh_token=refresh_token)


async def common_auth_procedure(
    user: User,
    client_ip: str,
    redis: Redis,  # type: ignore
    auth_settings: AuthSettings,
) -> TokenResponse:
    """
    Common authentication procedure for login and refresh token based on
    token generation
    :param user: The user to authenticate
    :type user: User
    :param client_ip: The IP address of the client
    :type client_ip: str
    :param redis: Dependency method for async Redis connection
    :type redis: Redis
    :param auth_settings: Dependency method for cached setting object
    :type auth_settings: AuthSettings
    :return: The token response object
    :rtype: TokenResponse
    """
    auth_token = AuthService.auth_token(user, auth_settings)
    user_info = f"{str(user.id)}:{client_ip}"
    token = TokenDB(key=auth_token.refresh_token, user_info=user_info)
    token_service = TokenService(redis, auth_settings)
    token_set = await token_service.create_token(token)
    if not token_set:
        detail = "Could not insert data in Authentication database"
        logger.warning(detail)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail
        )
    return TokenResponse(**auth_token.model_dump())
