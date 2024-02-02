"""
A module for region in the app-crud package.
"""

import logging

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.decorators import benchmark, with_logging
from app.db.session import get_session
from app.models.sql.region import Region

logger: logging.Logger = logging.getLogger(__name__)


class RegionRepository:
    """
    Repository for regions
    """

    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    @with_logging
    @benchmark
    async def get_region(self, _id: str) -> Region | None:
        """
        Get a region by id
        :param _id: The id of the region
        :type _id: str
        :return: The region object
        :rtype: Region
        """
        db_obj: Region | None = None
        async with self.session as async_session:
            try:
                db_obj = await async_session.get(Region, _id)
                logger.info("Retrieving region with id: %s", _id)
            except SQLAlchemyError as sa_exc:
                logger.error(sa_exc)
            return db_obj

    async def get_region_code_by_region(self, region: str) -> str | None:
        """
        Get the region code by the given region
        :param region: The region to search
        :type region: str
        :return: The region code
        :rtype: str
        """
        region_code: str | None = None
        async with self.session as async_session:
            stmt = select(Region).where(Region.region == region)
            try:
                region_code = await async_session.scalar(stmt)
                logger.info("Retrieving region code for region: %s", region)
            except SQLAlchemyError as sa_exc:
                logger.error(sa_exc)
            return region_code

    async def get_capital_by_region(self, region: str) -> str | None:
        """
        Get the capital by the given region
        :param region: The region to search
        :type region: str
        :return: The region's capital
        :rtype: str
        """
        async with self.session as session:
            stmt = select(Region).where(Region.region == region)
            try:
                capital: str | None = await session.scalar(stmt)
                logger.info("Retrieving capital for region: %s", region)
            except SQLAlchemyError as sa_exc:
                logger.error(sa_exc)
                raise sa_exc
            return capital


async def get_region_repository() -> RegionRepository:
    """
    Create a RegionRepository with an async database session.
    :return: A RegionRepository instance
    :rtype: RegionRepository
    """
    return RegionRepository(await get_session())
