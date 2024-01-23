"""
This script handles CRUD (Create, Read, Update, Delete) operations for
 Address objects in the database.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.decorators import benchmark, with_logging
from app.crud.filter import (
    IndexFilter,
    UniqueFilter,
    get_index_filter,
    get_unique_filter,
)
from app.crud.specification import IdSpecification
from app.db.session import get_session
from app.exceptions.exceptions import DatabaseException
from app.models.sql.address import Address as AddressDB
from app.schemas.external.address import Address, AddressUpdate

logger: logging.Logger = logging.getLogger(__name__)


class AddressRepository:
    """
    This class handles all operations (CRUD) related to an Address in the
     database.
    """

    def __init__(
        self,
        session: AsyncSession,
        index_filter: IndexFilter,
        unique_filter: UniqueFilter,
    ):
        self.session: AsyncSession = session
        self.index_filter: IndexFilter = index_filter
        self.unique_filter: UniqueFilter = unique_filter
        self.model: AddressDB = AddressDB  # type: ignore

    async def read_by_id(self, _id: IdSpecification) -> Optional[AddressDB]:
        """
        Retrieve an address from the database by its id
        :param _id: The id of the address
        :type _id: IdSpecification
        :return: The address with the specified id, or None if no such
            address exists
        :rtype: Optional[AddressDB]
        """
        async with self.session as session:
            try:
                address: AddressDB = await self.index_filter.filter(
                    _id, session, self.model
                )
            except SQLAlchemyError as db_exc:
                logger.error(db_exc)
                raise DatabaseException(str(db_exc)) from db_exc
            return address

    @with_logging
    @benchmark
    async def create_address(
        self,
        address: Address,
    ) -> AddressDB:
        """
        Create a new address in the database.
        :param address: An object containing the information of the address
         to create
        :type address: Address
        :return: The created address object
        :rtype: AddressDB
        """
        address_create: AddressDB = AddressDB(**address.model_dump())
        async with self.session as session:
            try:
                session.add(address_create)
                await session.commit()
            except SQLAlchemyError as sa_exc:
                logger.error(sa_exc)
                raise DatabaseException(str(sa_exc)) from sa_exc
            return address_create

    @with_logging
    @benchmark
    async def update_address(
        self, address_id: IdSpecification, address: AddressUpdate
    ) -> Address:
        """
        Update the information of an address in the database
        :param address_id: The id of the address to update
        :type address_id: IdSpecification
        :param address: An object containing the new information of the
         address
        :type address: AddressUpdate
        :return: The updated address, or None if no such address exists
        :rtype: Address
        """
        async with self.session as session:
            try:
                found_address: Optional[AddressDB] = await self.read_by_id(
                    address_id
                )
            except DatabaseException as db_exc:
                logger.error(db_exc)
                raise DatabaseException(str(db_exc)) from db_exc
            if not found_address:
                raise DatabaseException(
                    f"Address with address_id: {address_id} could not be "
                    f"updated"
                )
            obj_data: dict[str, Any] = jsonable_encoder(found_address)
            update_data: dict[str, Any] = address.model_dump(exclude_unset=True)
            for field in obj_data:
                if field in update_data:
                    setattr(found_address, field, update_data[field])
                if field == "updated_at":
                    setattr(found_address, field, datetime.now(timezone.utc))
            session.add(found_address)
            await session.commit()
            try:
                address_db: Optional[AddressDB] = await self.read_by_id(
                    address_id
                )
                if not address_db:
                    raise DatabaseException(
                        f"Address with ID {address_id} not found"
                    )
                updated_address: Address = Address.model_validate(address_db)
            except DatabaseException as db_exc:
                logger.error(db_exc)
                raise DatabaseException(str(db_exc)) from db_exc
            return updated_address


async def get_address_repository() -> AddressRepository:
    """
    Create a AddressRepository with an async database session, an index
     filter, and a unique filter.
    :return: A AddressRepository instance
    :rtype: AddressRepository
    """
    return AddressRepository(
        await get_session(), await get_index_filter(), await get_unique_filter()
    )
