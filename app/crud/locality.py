"""
A module for locality in the app-crud package.
"""

import logging

from pydantic import PositiveInt
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.decorators import benchmark, with_logging
from app.db.session import get_session
from app.models.sql.locality import Locality

logger: logging.Logger = logging.getLogger(__name__)


class LocalityRepository:
    """
    Repository for locality model
    """

    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    @with_logging
    @benchmark
    async def get_locality(self, _id: PositiveInt) -> Locality | None:
        """
        Get the locality by the given id
        :param _id: The id of the locality
        :type _id: PositiveInt
        :return: The locality object
        :rtype: Locality
        """
        async with self.session as async_session:
            locality: Locality | None = None
            try:
                locality = await async_session.get(Locality, _id)
                logger.info("Retrieving locality with id: %s", _id)
            except SQLAlchemyError as sa_exc:
                logger.error(sa_exc)
            return locality

    @with_logging
    @benchmark
    async def get_locality_by_name(self, name: str) -> Locality | None:
        """
        Get the locality object given its name
        :param name: The name of the city
        :type name: str
        :return: The locality object
        :rtype: Locality
        """
        async with self.session as async_session:
            stmt = select(Locality).where(Locality.locality == name)
            try:
                locality: Locality = await async_session.scalar(stmt)
                logger.info("Retrieving locality with name: %s", name)
            except SQLAlchemyError as sa_exc:
                logger.error(sa_exc)
                return None
            return locality


async def get_locality_repository() -> LocalityRepository:
    """
    Create a LocalityRepository with an async database session.
    :return: A LocalityRepository instance
    :rtype: LocalityRepository
    """
    return LocalityRepository(await get_session())
