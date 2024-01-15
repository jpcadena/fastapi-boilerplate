"""
A module for user schema in the app schemas package.
"""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from pydantic_extra_types.phone_numbers import PhoneNumber

from app.schemas.external.address import Address
from app.schemas.infrastructure.gender import Gender
from app.schemas.infrastructure.user import UserAuth, UserBase, UserInDB
from app.schemas.infrastructure.user_base import (
    UserID,
    UserName,
    UserOptional,
    UserPassword,
    UserUpdatedAt,
)
from app.schemas.schemas import (
    user_create_example,
    user_create_response_example,
    user_example,
    user_response_example,
    user_super_create_example,
    user_update_example,
    user_update_response_example,
)
from app.utils.utils import validate_password, validate_phone_number


class UserCreate(UserBase, UserOptional):
    """
    Schema for creating a User record.
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra=user_create_example,
    )

    password: str = Field(
        ...,
        title="Password",
        description="Password of the User",
        min_length=8,
        max_length=14,
    )

    @field_validator("password", mode="before")
    def validate_password(cls, v: Optional[str]) -> str:
        """
        Validates the password attribute
        :param v: The password to be validated
        :type v: Optional[str]
        :return: The validated password
        :rtype: str
        """
        # pylint: disable=no-self-argument
        return validate_password(v)


class UserSuperCreate(UserCreate):
    """
    Schema for creating a superuser.
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra=user_super_create_example,
    )

    is_superuser: bool = Field(
        default=True,
        title="Is super user?",
        description="True if the user is super user; otherwise false",
    )


class UserCreateResponse(UserID, UserBase):
    """
    Schema for the response when creating a User.
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra=user_create_response_example,
    )


class UserUpdate(BaseModel):
    """
    Schema for updating a User record.
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra=user_update_example,
    )

    username: Optional[str] = Field(
        default=None,
        title="Username",
        description="Username to identify the user",
        min_length=4,
        max_length=15,
    )
    email: Optional[EmailStr] = Field(
        default=None,
        title="Email",
        description="Preferred e-mail address of the User",
    )
    first_name: Optional[str] = Field(
        default=None,
        title="First name",
        description="First name(s) of the User",
        min_length=1,
        max_length=50,
    )
    middle_name: Optional[str] = Field(
        default=None,
        title="Middle Name",
        description="Middle name(s) of the User",
        max_length=50,
    )
    last_name: Optional[str] = Field(
        default=None,
        title="Last name",
        description="Last name(s) of the User",
        min_length=1,
        max_length=100,
    )
    password: Optional[str] = Field(
        default=None,
        title="New Password",
        description="New Password of the User",
        min_length=8,
        max_length=14,
    )
    gender: Optional[Gender] = Field(
        default=None, title="Gender", description="Gender of the User"
    )
    birthdate: Optional[date] = Field(
        default=None, title="Birthdate", description="Birthday of the User"
    )
    phone_number: Optional[PhoneNumber] = Field(
        default=None,
        title="Phone number",
        description="Preferred telephone number of the User",
    )
    address: Optional[Address] = Field(
        default=None, title="Address", description="Address of the User"
    )

    @field_validator("password", mode="before")
    def validate_password(cls, v: Optional[str]) -> str:
        """
        Validates the password attribute
        :param v: The password value to validate
        :type v: Optional[str]
        :return: The validated password
        :rtype: str
        """
        # pylint: disable=no-self-argument
        return validate_password(v)

    @field_validator("phone_number", mode="before")
    def validate_phone_number(
        cls, v: Optional[PhoneNumber]
    ) -> Optional[PhoneNumber]:
        """
        Validates the phone number attribute
        :param v: The phone number value to validate
        :type v: Optional[PhoneNumber]
        :return: The validated phone number
        :rtype: Optional[PhoneNumber]
        """
        return validate_phone_number(v)


class UserUpdateResponse(
    UserAuth, UserName, UserPassword, UserOptional, UserInDB
):
    """
    Schema for the response when updating a User.
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra=user_update_response_example,
    )


class User(UserBase, UserOptional, UserUpdatedAt):
    """
    Schema for representing a User.
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra=user_example,
    )

    password: str = Field(
        ...,
        title="Hashed Password",
        description="Hashed Password of the User",
        min_length=60,
        max_length=60,
    )
    is_active: bool = Field(
        default=True,
        title="Is active?",
        description="True if the user is active; otherwise false",
    )
    is_superuser: bool = Field(
        default=False,
        title="Is super user?",
        description="True if the user is super user; otherwise false",
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        title="Created at",
        description="Time the User was created",
    )


class UserResponse(UserID, UserBase, UserOptional, UserInDB):
    """
    Schema for the response when retrieving a User.
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra=user_response_example,
    )


class UsersResponse(BaseModel):
    """
    Class representation for a list of users response
    """

    users: list[UserResponse]
