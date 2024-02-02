"""
A module for token in the app.services package.
"""

import logging

from pydantic import PositiveInt
from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.config.db.auth_settings import AuthSettings
from app.core.decorators import benchmark
from app.db.auth import handle_redis_exceptions
from app.models.unstructured.token import Token

logger: logging.Logger = logging.getLogger(__name__)


class TokenService:
    """
    Service class for token operations in the authentication database
    """

    def __init__(
        self,
        redis: Redis,  # type: ignore
        auth_settings: AuthSettings,
    ):
        self._redis: Redis = redis  # type: ignore
        self._refresh_token_expire_minutes: PositiveInt = (
            auth_settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )
        self._blacklist_expiration_seconds: PositiveInt = (
            PositiveInt(
                PositiveInt(auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES) + 1
            )
            * 60
        )  # converting minutes to seconds

    @handle_redis_exceptions
    @benchmark
    async def create_token(self, token: Token) -> bool:
        """
        Create a token in authentication database
        :param token: Token object with key and value
        :type token: Token
        :return: True if the token was inserted; otherwise false
        :rtype: bool
        """
        try:
            inserted: bool = await self._redis.setex(
                token.key,
                self._refresh_token_expire_minutes,
                token.user_info,
            )
        except RedisError as r_exc:
            logger.error("Error at creating token. %s", r_exc)
            raise r_exc
        return inserted

    @handle_redis_exceptions
    @benchmark
    async def get_token(self, key: str) -> str | None:
        """
        Read token from the authentication database
        :param key: The key to search for
        :type key: str
        :return: The refresh token
        :rtype: str
        """
        try:
            value: str = str(await self._redis.get(key))
        except RedisError as r_exc:
            logger.error("Error at getting token. %s", r_exc)
            raise r_exc
        return value

    @handle_redis_exceptions
    @benchmark
    async def blacklist_token(self, token_key: str) -> bool:
        """
        Blacklist a given token.
        :param token_key: The token key to blacklist.
        :type token_key: str
        :return: True if the token was successfully blacklisted,
         otherwise False.
        :rtype: bool
        """
        try:
            blacklisted: bool = await self._redis.setex(
                f"blacklist:{token_key}",
                self._blacklist_expiration_seconds,
                "true",
            )
        except RedisError as r_exc:
            logger.error("Error at blacklisting token. %s", r_exc)
            raise r_exc
        return blacklisted

    @handle_redis_exceptions
    @benchmark
    async def is_token_blacklisted(self, token_key: str) -> bool:
        """
        Check if a given token is blacklisted.
        :param token_key: The token key to verify.
        :type token_key: str
        :return: True if the token is blacklisted, otherwise False.
        :rtype: bool
        """
        try:
            blacklisted: str | None = await self._redis.get(
                f"blacklist" f":{token_key}"
            )
        except RedisError as r_exc:
            logger.error("Error at checking if token is blacklisted. %s", r_exc)
            raise r_exc
        return bool(blacklisted)
