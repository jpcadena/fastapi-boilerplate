"""
A module for oauth2 validation in the app.api package.
"""
from typing import Any, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio import Redis

from app.api.deps import get_redis_dep
from app.config.config import auth_setting, get_auth_settings
from app.config.db.auth_settings import AuthSettings
from app.exceptions.exceptions import raise_unauthorized_error
from app.models.sql.user import User
from app.schemas.external.user import UserAuth
from app.services.infrastructure.token import TokenService
from app.services.infrastructure.user import (
    CachedUserService,
    UserService,
    get_user_service,
)
from app.utils.security.jwt import decode_jwt

oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(
    tokenUrl=auth_setting.TOKEN_URL,
    scheme_name="JWT",
    description="JWT token used to authenticate most of the API endpoints.",
)
refresh_token_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(
    tokenUrl="api/v1/auth/refresh",
    scheme_name="JWT",
    description="JWT token used specifically for refreshing access tokens.",
)


async def authenticate_user(
    token: str,
    auth_settings: AuthSettings,
    user_service: UserService,
    redis: Redis,  # type: ignore
) -> UserAuth:
    """
    Authenticates a user based on the provided token (access or refresh token)
    :param token: JWT token from OAuth2PasswordBearer
    :type token: str
    :param auth_settings: Dependency method for cached setting object
    :type auth_settings: AuthSettings
    :param user_service: Dependency method for User service object
    :type user_service: UserService
    :param redis: Dependency method for async Redis connection
    :type redis: Redis
    :return: Authenticated user information
    :rtype: UserAuth
    """
    payload: dict[str, Any] = decode_jwt(token, auth_settings)
    username: str = payload.get("preferred_username")  # type: ignore
    sub: str = payload.get("sub")  # type: ignore
    if username is None or sub is None:
        await raise_unauthorized_error(
            auth_settings.DETAIL, auth_settings.HEADERS
        )
    user_id: UUID = UUID(sub.replace("username:", ""))
    cached_service: CachedUserService = CachedUserService(redis)
    cached_user: Optional[User] = await cached_service.get_model_from_cache(
        user_id
    )
    if cached_user:
        return UserAuth(**cached_user.__dict__)
    user: User = await user_service.get_login_user(username)
    user_auth: UserAuth = UserAuth(**user.__dict__)
    await cached_service.set_to_cache(user_id, user_auth.model_dump())
    return user_auth


async def get_refresh_current_user(
    refresh_token: str = Depends(refresh_token_scheme),
    auth_settings: AuthSettings = Depends(get_auth_settings),
    user_service: UserService = Depends(get_user_service),
    redis: Redis = Depends(get_redis_dep),  # type: ignore
) -> UserAuth:
    """
    Fetches the current authenticated user based on the provided JWT
     refresh token
    :param refresh_token: The Refresh token from OAuth2PasswordBearer
    :type refresh_token: str
    :param auth_settings: Dependency method for cached setting object
    :type auth_settings: AuthSettings
    :param user_service: Dependency method for User service object
    :type user_service: UserService
    :param redis: Dependency method for async Redis connection
    :type redis: Redis
    :return: Authenticated user information
    :rtype: UserAuth
    """
    return await authenticate_user(
        refresh_token, auth_settings, user_service, redis
    )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_settings: AuthSettings = Depends(get_auth_settings),
    user_service: UserService = Depends(get_user_service),
    redis: Redis = Depends(get_redis_dep),  # type: ignore
) -> UserAuth:
    """
    Fetches the current authenticated user based on the provided JWT
     access token
    :param token: The Access token from OAuth2PasswordBearer
    :type token: str
    :param auth_settings: Dependency method for cached setting object
    :type auth_settings: AuthSettings
    :param user_service: Dependency method for User service object
    :type user_service: UserService
    :param redis: Dependency method for async Redis connection
    :type redis: Redis
    :return: Authenticated user information
    :rtype: UserAuth
    """
    token_service: TokenService = TokenService(redis, auth_settings)
    is_blacklisted: bool = await token_service.is_token_blacklisted(token)
    if is_blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is blacklisted",
        )
    return await authenticate_user(token, auth_settings, user_service, redis)
