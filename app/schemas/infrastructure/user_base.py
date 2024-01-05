"""
A module for user base in the app.schemas.infrastructure package.
"""
from datetime import date, datetime
from typing import Optional

from pydantic import UUID4, BaseModel, ConfigDict, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber

from app.schemas.external.address import Address
from app.schemas.infrastructure.gender import Gender
from app.schemas.schemas import (
    id_example,
    updated_at_example,
    user_base_auth_example,
    user_optional_example,
    user_password_example,
    username_example,
)


class UserID(BaseModel):
    """
    Schema for representing a User's ID.
    """

    model_config = ConfigDict(
        json_schema_extra=id_example,
    )

    id: UUID4 = Field(
        default_factory=UUID4, title="ID", description="ID of the User"
    )


class UserUpdatedAt(BaseModel):
    """
    Schema for representing the update timestamp of a User.
    """

    model_config = ConfigDict(
        json_schema_extra=updated_at_example,
    )

    updated_at: Optional[datetime] = Field(
        default=None,
        title="Updated at",
        description="Time the User was updated",
    )


class UserPassword(BaseModel):
    """
    Schema for representing a User's password.
    """

    model_config = ConfigDict(
        json_schema_extra=user_password_example,
    )

    password: str = Field(
        ...,
        title="Hashed Password",
        description="Hashed Password of the User",
        min_length=60,
        max_length=60,
    )


class UserOptional(BaseModel):
    """
    Schema for representing a User with optional attributes.
    """

    model_config = ConfigDict(
        json_schema_extra=user_optional_example,
    )

    middle_name: Optional[str] = Field(
        default=None,
        title="Middle Name",
        description="Middle name(s) of the User",
        max_length=50,
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


class UserBaseAuth(BaseModel):
    """
    Schema for representing the basic authentication attributes of a
     User.
    """

    model_config = ConfigDict(
        json_schema_extra=user_base_auth_example,
    )

    username: str = Field(
        ...,
        title="Username",
        description="Username to identify the user",
        min_length=4,
        max_length=15,
    )
    email: EmailStr = Field(
        ..., title="Email", description="Preferred e-mail address of the User"
    )


class UserName(BaseModel):
    """
    Schema for representing the name attributes of a User.
    """

    model_config = ConfigDict(
        json_schema_extra=username_example,
    )

    first_name: str = Field(
        ...,
        title="First name",
        description="First name(s) of the User",
        min_length=4,
        max_length=50,
    )
    last_name: str = Field(
        ...,
        title="Last name",
        description="Last name(s) of the User",
        min_length=4,
        max_length=100,
    )
