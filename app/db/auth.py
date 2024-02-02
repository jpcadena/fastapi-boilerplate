"""
This script provides functions for interacting with the authentication
 (Redis) database.
"""

import logging
from collections.abc import Callable
from typing import Any

from redis.exceptions import (AuthenticationError,
                              ConnectionError as RedisConnectionError,
                              DataError, NoPermissionError,
                              TimeoutError as RedisTimeoutError
                              )

from app.exceptions.exceptions import ServiceException

logger: logging.Logger = logging.getLogger(__name__)


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
