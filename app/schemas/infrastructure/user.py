"""
A module for user in the app.schemas.infrastructure package.
"""

from datetime import datetime

from pydantic import ConfigDict, Field

from app.schemas.infrastructure.user_base import (
    UserBaseAuth,
    UserID,
    UserName,
    UserUpdatedAt,
)
from app.schemas.schemas import (
    user_auth_example,
    user_base_example,
    user_in_db_example,
)


class UserBase(UserBaseAuth, UserName):
    """
    Base schema for representing a User.
    """

    model_config = ConfigDict(
        json_schema_extra=user_base_example,
    )


class UserAuth(UserID, UserBaseAuth):
    """
    User Auth that inherits from UserID.
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra=user_auth_example,
    )


class UserInDB(UserUpdatedAt):
    """
    Schema for representing a User record in the database.
    """

    model_config = ConfigDict(
        json_schema_extra=user_in_db_example,
    )

    is_active: bool = Field(
        ...,
        title="Is active?",
        description="True if the user is active; otherwise false",
    )
    is_superuser: bool = Field(
        ...,
        title="Is super user?",
        description="True if the user is super user; otherwise false",
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        title="Created at",
        description="Time the User was created",
    )
