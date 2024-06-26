"""
User Service to handle business logic
"""

import logging
from datetime import datetime
from typing import Annotated, Any

from fastapi import Depends
from pydantic import UUID4, EmailStr, NonNegativeInt, PositiveInt
from redis.asyncio import Redis

from app.api.deps import get_redis_dep
from app.crud.specification import (
    EmailSpecification,
    IdSpecification,
    UsernameSpecification,
)
from app.crud.user import UserRepository, get_user_repository
from app.exceptions.exceptions import (
    DatabaseException,
    NotFoundException,
    ServiceException,
)
from app.models.sql.user import User
from app.schemas.external.user import (
    UserCreate,
    UserCreateResponse,
    UserResponse,
    UserSuperCreate,
    UserUpdate,
    UserUpdateResponse,
)

logger: logging.Logger = logging.getLogger(__name__)


class UserService:
    """
    Service class for user-related business logic.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        redis: Redis,  # type: ignore
    ):
        self._user_repo: UserRepository = user_repo
        self._redis: Redis = redis  # type: ignore

    async def get_user_by_id(self, user_id: UUID4) -> UserResponse | None:
        """
        Retrieve user information by its unique identifier
        :param user_id: The unique identifier of the user
        :type user_id: UUID4
        :return: User information
        :rtype: Optional[UserResponse]
        """
        user: User | None
        try:
            user = await self._user_repo.read_by_id(IdSpecification(user_id))
        except DatabaseException as db_exc:
            logger.error(str(db_exc))
            raise ServiceException(str(db_exc)) from db_exc
        if not user:
            detail: str = f"User with id {user_id} not found in the system."
            logger.error(detail)
            raise NotFoundException(detail)
        user_response: UserResponse = UserResponse.model_validate(user)
        return user_response

    async def get_login_user(self, username: str) -> User:
        """
        Retrieve user information for login purposes by its username
        :param username: The username to retrieve User from
        :type username: str
        :return: User information
        :rtype: User
        """
        try:
            user: User | None = await self._user_repo.read_by_username(
                UsernameSpecification(username)
            )
        except DatabaseException as db_exc:
            logger.error(str(db_exc))
            raise ServiceException(str(db_exc)) from db_exc
        if not user:
            raise ServiceException(f"User not found with username: {username}")
        return user

    async def get_user_by_email(self, email: EmailStr) -> UserResponse:
        """
        Retrieve user information by its unique email.
        :param email: The email to retrieve User from
        :type email: EmailStr
        :return: User found in database
        :rtype: UserResponse
        """
        try:
            user: User | None = await self._user_repo.read_by_email(
                EmailSpecification(email)
            )
        except DatabaseException as db_exc:
            logger.error(str(db_exc))
            raise ServiceException(str(db_exc)) from db_exc
        if not user:
            raise ServiceException(f"User not found with email: {email}")
        return UserResponse.model_validate(user)

    async def register_user(
        self, user: UserCreate | UserSuperCreate
    ) -> UserCreateResponse:
        """
        Register a new user in the database
        :param user: Request object representing the user
        :type user: Union[UserCreate, UserSuperCreate]
        :return: Response object representing the created user in the
         database
        :rtype: UserCreateResponse
        """
        try:
            created_user = await self._user_repo.create_user(user)
        except DatabaseException as db_exc:
            logger.error(str(db_exc))
            raise ServiceException(str(db_exc)) from db_exc
        return UserCreateResponse.model_validate(created_user)

    async def get_users(
        self, offset: NonNegativeInt | None, limit: PositiveInt | None
    ) -> list[UserResponse]:
        """
        Retrieve users' information from the table
        :param offset: Offset from where to start returning users
        :type offset: NonNegativeInt
        :param limit: Limit the number of results from query
        :type limit: PositiveInt
        :return: User information
        :rtype: list[UserResponse]
        """
        try:
            users: list[User] = await self._user_repo.read_users(offset, limit)
        except DatabaseException as db_exc:
            logger.error(str(db_exc))
            raise ServiceException(str(db_exc)) from db_exc
        found_users: list[UserResponse] = [
            UserResponse.model_validate(user) for user in users
        ]
        return found_users

    async def update_user(
        self, user_id: UUID4, user: UserUpdate
    ) -> UserUpdateResponse:
        """
        Update user information from table
        :param user_id: Unique identifier of the user
        :type user_id: UUID4
        :param user: Requested user information to update
        :type user: UserUpdate
        :return: User information
        :rtype: UserUpdateResponse
        """
        try:
            updated_user: User | None = await self._user_repo.update_user(
                IdSpecification(user_id), user
            )
        except DatabaseException as db_exc:
            logger.error(str(db_exc))
            raise ServiceException(str(db_exc)) from db_exc
        if not updated_user:
            raise ServiceException(
                f"User with user_id: {user_id} could not be updated"
            )
        return UserUpdateResponse.model_validate(updated_user)

    async def delete_user(self, user_id: UUID4) -> dict[str, Any]:
        """
        Deletes a user by its id
        :param user_id: Unique identifier of the user
        :type user_id: UUID4
        :return: Data to confirmation info about the delete process
        :rtype: dict[str, Any]
        """
        deleted: bool = False
        deleted_at: datetime | None = None
        try:
            deleted = await self._user_repo.delete_user(
                IdSpecification(user_id)
            )
            deleted_at = datetime.now() if deleted else None
        except DatabaseException as db_exc:
            logger.error(str(db_exc))
        finally:
            return {"ok": deleted, "deleted_at": deleted_at}


async def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    redis: Annotated[Redis, Depends(get_redis_dep)],  # type: ignore
) -> UserService:
    """
    Get an instance of the user service with the given repository.
    :param user_repo: User repository object for database connection
    :type user_repo: UserRepository
    :param redis: Dependency method for async Redis connection
    :type redis: Redis
    :return: UserService instance with repository associated
    :rtype: UserService
    """
    return UserService(user_repo, redis)
