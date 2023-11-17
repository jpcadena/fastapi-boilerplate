"""
A module for lifecycle in the app-core package.
"""
import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI

from app.api.deps import RedisConnectionManager
from app.config.config import auth_setting, init_setting, setting
from app.crud.user import get_user_repository
from app.db.init_db import init_db

logger: logging.Logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[Any, None]:
    """
    The lifespan of the application
    :param application: The FastAPI application
    :type application: FastAPI
    :return: An asynchronous generator for the application
    :rtype: AsyncGenerator[Any, None]
    """
    redis_manager: RedisConnectionManager = RedisConnectionManager(auth_setting)
    logger.info("Starting API...")
    await init_db(await get_user_repository(), setting, init_setting)
    async with redis_manager.connection() as connection:
        application.state.redis_connection = connection
        yield
