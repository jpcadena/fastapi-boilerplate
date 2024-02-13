"""
A module for cached user in the app.services.infrastructure package.
"""

import json
from typing import Any

from pydantic import UUID4, PositiveInt
from redis.asyncio import Redis

from app.config.config import auth_setting
from app.models.sql.address import Address as AddressDB
from app.models.sql.user import User
from app.schemas.external.address import Address
from app.schemas.external.user import UserResponse
from app.schemas.schemas import custom_serializer


class CachedUserService:
    """
    Service class for cached user-related business logic.
    """

    def __init__(
        self,
        redis: Redis,  # type: ignore
    ):
        self._redis: Redis = redis  # type: ignore
        self._cache_seconds: PositiveInt = auth_setting.CACHE_SECONDS

    async def get_model_from_cache(self, key: UUID4) -> User | None:
        """
        Get the user model instance for the given key from the cache database
        :param key: The unique identifier for the model user instance
        :type key: UUID4
        :return: The user model instance
        :rtype: User
        """
        value: str | None = await self._redis.get(str(key))
        if not value:
            return None
        user_data: dict[str, Any] = json.loads(value)
        address_data: dict[str, Any] = user_data.pop("address", {})
        if address_data is not None:
            address_instance: Address = Address(**address_data)
            address_create: AddressDB = AddressDB(
                **address_instance.model_dump()
            )
            user_instance: User = User(address=address_create, **user_data)
            return user_instance
        return None

    async def get_schema_from_cache(self, key: UUID4) -> UserResponse | None:
        """
        Get the user auth schema instance for the given key from the cache
        database
        :param key: The unique identifier for the user instance
        :type key: UUID4
        :return: The user schema instance
        :rtype: UserResponse
        """
        value: str | None = await self._redis.get(str(key))
        if value:
            user_data: dict[str, Any] = json.loads(value)
            if len(user_data.keys()) > 3:
                return UserResponse(**user_data)
        return None

    async def set_to_cache(
        self,
        key: UUID4,
        value: dict[str, Any],
    ) -> None:
        """
        Set the user schema instance to the cache database using the given key
        :param key: The unique identifier for the user instance
        :type key: UUID4
        :param value: The user schema instance to be used
        :type value: dict[str, Any]
        :return: None
        :rtype: NoneType
        """
        await self._redis.setex(
            str(key), self._cache_seconds, json.dumps(custom_serializer(value))
        )
