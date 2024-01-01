"""
This script provides functions for interacting with the authentication
 (Redis) database.
"""
import logging
from typing import Annotated, Any, Callable

from fastapi import Depends
from redis.asyncio import Redis
from redis.exceptions import AuthenticationError
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import DataError, NoPermissionError
from redis.exceptions import TimeoutError as RedisTimeoutError

from app.config.config import get_auth_settings
from app.config.db.auth_settings import AuthSettings
from app.core.decorators import benchmark, with_logging
from app.exceptions.exceptions import ServiceException

logger: logging.Logger = logging.getLogger(__name__)


@with_logging
@benchmark
async def init_auth_db(
    auth_settings: Annotated[AuthSettings, Depends(get_auth_settings)],
) -> None:
    """
    Initialize connection to the Redis database for authentication
    :param auth_settings: Dependency method for cached setting object
    :type auth_settings: AuthSettings
    :return: None
    :rtype: NoneType
    """
    url: str = auth_settings.REDIS_DATABASE_URI.__str__()
    redis_pool = Redis.from_url(url, decode_responses=True)
    await redis_pool.ping()
    logger.info("Redis Database initialized")


def handle_redis_exceptions(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator for handling Redis exceptions
    :param func: The function to be decorated
    :type func: Callable[..., Any]
    :return: The decorated function.
    :rtype: Callable[..., Any]
    """

    async def inner(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Any:
        """
        Inner function to handle Redis exceptions.
        :param args: The arguments to be decorated.
        :type args: tuple[Any, ...]
        :param kwargs: The keyword arguments to be decorated.
        :type kwargs: dict[str, Any]
        :return: The return value of the function or None if an
         exception occurs.
        :rtype: Any
        """
        try:
            return await func(*args, **kwargs)
        except (
            AuthenticationError,
            RedisConnectionError,
            DataError,
            NoPermissionError,
            RedisTimeoutError,
        ) as exc:
            logger.error("Redis error occurred: %s", exc)
            raise ServiceException(
                f"An error occurred while processing the Redis operation.\n"
                f"{exc}"
            ) from exc

    return inner
