"""
This script handles CRUD (Create, Read, Update, Delete) operations for
 User objects in the database.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Optional, Union

from pydantic import UUID4, NonNegativeInt, PositiveInt
from sqlalchemy import select
from sqlalchemy.engine import Result, ScalarResult
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.config.config import setting
from app.core.decorators import benchmark, with_logging
from app.core.security.password import get_password_hash
from app.crud.filter import (
    IndexFilter,
    UniqueFilter,
    get_index_filter,
    get_unique_filter,
)
from app.crud.specification import (
    EmailSpecification,
    IdSpecification,
    UsernameSpecification,
)
from app.db.session import get_session
from app.exceptions.exceptions import DatabaseException
from app.models.sql.address import Address
from app.models.sql.user import User
from app.schemas.external.address import AddressUpdate
from app.schemas.external.user import UserCreate, UserSuperCreate, UserUpdate

logger: logging.Logger = logging.getLogger(__name__)


class UserRepository:
    """
    This class handles all operations (CRUD) related to a User in the
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
        self.model: User = User  # type: ignore
        # self._encryption_service: EncryptionService = get_encryption_service()

    async def read_by_id(self, _id: IdSpecification) -> Optional[User]:
        """
        Retrieve a user from the database by its id
        :param _id: The id of the user
        :type _id: IdSpecification
        :return: The user with the specified id, or None if no such
            user exists
        :rtype: Optional[User]
        """
        async with self.session as session:
            try:
                user: User = await self.index_filter.filter(
                    _id, session, self.model
                )
            except SQLAlchemyError as db_exc:
                logger.error(db_exc)
                raise DatabaseException(str(db_exc)) from db_exc
            return user

    async def read_by_username(
        self, username: UsernameSpecification
    ) -> Optional[User]:
        """
        Retrieve a user from the database by its username
        :param username: The username of the user
        :type username: UsernameSpecification
        :return: The user with the specified username
        :rtype: Optional[User]
        """
        async with self.session as session:
            try:
                user: User = await self.unique_filter.filter(
                    username, session, self.model, "username"
                )
            except SQLAlchemyError as db_exc:
                logger.error(db_exc)
                raise DatabaseException(str(db_exc)) from db_exc
            return user

    async def read_by_email(self, email: EmailSpecification) -> Optional[User]:
        """
        Retrieve a user from the database by its email
        :param email: The email of the user
        :type email: EmailSpecification
        :return: The user with the specified email, or None if no such
         user exists
        :rtype: Optional[User]
        """
        async with self.session as session:
            try:
                user: Optional[User] = await self.unique_filter.filter(
                    email, session, self.model, "email"
                )
            except SQLAlchemyError as db_exc:
                logger.error(db_exc)
                if email.value != setting.SUPERUSER_EMAIL:
                    raise DatabaseException(str(db_exc)) from db_exc
                logger.warning("Not raising exception for SUPERUSER")
                user = None
            return user

    @with_logging
    @benchmark
    async def read_users(
        self,
        offset: NonNegativeInt,
        limit: PositiveInt,
    ) -> list[User]:
        """
        Retrieve a list of users from the database, with pagination
        :param offset: The number of users to skip before starting to
         return users
        :type offset: NonNegativeInt
        :param limit: The maximum number of users to return
        :type limit: PositiveInt
        :return: A list of users
        :rtype: list[User]
        """
        stmt: Select = select(User).offset(offset).limit(limit)
        async with self.session as session:
            try:
                results: ScalarResult = await session.scalars(stmt)
                users: list[User] = results.all()
            except SQLAlchemyError as sa_exc:
                logger.error(sa_exc)
                raise DatabaseException(str(sa_exc)) from sa_exc
            return users

    async def read_id_by_email(self, email: EmailSpecification) -> UUID4:
        """
        Retrieve a user's id from the database by the user's email
        :param email: The email of the user
        :type email: EmailSpecification
        :return: The id of the user with the specified email, or None
         if no such user exists
        :rtype: Optional[UUID4]
        """
        async with self.session as session:
            try:
                stmt: Select = select(User.id).where(
                    self.model.email == email.value
                )
                result: Result = await session.execute(stmt)
                user_id: Optional[UUID4] = result.scalar()
            except SQLAlchemyError as db_exc:
                logger.error(db_exc)
                raise DatabaseException(str(db_exc)) from db_exc
            if not user_id:
                raise DatabaseException(
                    f"User with email: {email} could not be found"
                )
            return user_id

    @with_logging
    @benchmark
    async def create_user(
        self,
        user: Union[UserCreate, UserSuperCreate],
    ) -> User:
        """
        Create a new user in the database.
        :param user: An object containing the information of the user
         to create
        :type user: Union[UserCreate, UserSuperCreate]
        :return: The created user object
        :rtype: User
        """
        address_data: dict[str, Any] = user.model_dump().pop("address")
        address: Address = Address(**address_data)
        hashed_password: str = get_password_hash(user.password)
        user_in = user.model_copy(
            update={
                "password": hashed_password,
                "address_id": address.id,
            }
        )
        user_data: dict[str, Any] = user_in.model_dump()
        user_data["address"] = address
        user_create: User = User(**user_data)
        async with self.session as session:
            try:
                session.add(user_create)
                await session.commit()
            except SQLAlchemyError as sa_exc:
                logger.error(sa_exc)
                await session.rollback()
                raise DatabaseException(str(sa_exc)) from sa_exc
            created_user: Optional[User] = await self.read_by_id(
                IdSpecification(user_create.id)
            )
            if not created_user:
                raise DatabaseException("User could not be created")
            return created_user

    async def update_user(
        self, user_id: IdSpecification, user: UserUpdate
    ) -> Optional[User]:
        """
        Update the information of a user in the database
        :param user_id: The id of the user to update
        :type user_id: IdSpecification
        :param user: An object containing the new information of the
         user
        :type user: UserUpdate
        :return: The updated user, or None if no such user exists
        :rtype: Optional[User]
        """
        async with self.session as session:
            try:
                found_user: Optional[User] = await self.read_by_id(user_id)
            except DatabaseException as db_exc:
                logger.error(db_exc)
                raise DatabaseException(str(db_exc)) from db_exc
            if not found_user:
                raise DatabaseException(
                    f"User with user_id: {user_id} could not be updated"
                )
            update_data: dict[str, Any] = user.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if value is not None:
                    if field == "password":
                        setattr(found_user, field, get_password_hash(value))
                    elif field == "address":
                        address_update = AddressUpdate(**value)
                        for (
                            address_field,
                            address_value,
                        ) in address_update.model_dump().items():
                            setattr(
                                found_user.address, address_field, address_value
                            )
                    else:
                        setattr(found_user, field, value)
            found_user.updated_at = datetime.now(timezone.utc)
            session.add(found_user)
            await session.commit()
            try:
                updated_user: Optional[User] = await self.read_by_id(user_id)
            except DatabaseException as db_exc:
                logger.error(db_exc)
                raise DatabaseException(str(db_exc)) from db_exc
            return updated_user

    @with_logging
    @benchmark
    async def delete_user(self, user_id: IdSpecification) -> bool:
        """
        Delete a user from the database
        :param user_id: The id of the user to delete
        :type user_id: IdSpecification
        :return: True if the user is deleted; otherwise False
        :rtype: bool
        """
        async with self.session as session:
            try:
                found_user: Optional[User] = await self.read_by_id(user_id)
            except DatabaseException as db_exc:
                raise DatabaseException(str(db_exc)) from db_exc
            if not found_user:
                raise DatabaseException(
                    f"User with user_id: {user_id} could not be deleted"
                )
            try:
                await session.delete(found_user)
                await session.commit()
            except SQLAlchemyError as sa_exc:
                logger.error(sa_exc)
                await session.rollback()
                return False
            return True


async def get_user_repository() -> UserRepository:
    """
    Create a UserRepository with an async database session, an index
     filter, and a unique filter.
    :return: A UserRepository instance
    :rtype: UserRepository
    """
    return UserRepository(
        await get_session(),
        await get_index_filter(),
        await get_unique_filter(),
    )
