"""
A module for user base in the app.schemas.infrastructure package.
"""

from datetime import date, datetime

from pydantic import (
    UUID4,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)
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
from app.utils.utils import validate_phone_number


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

    updated_at: datetime | None = Field(
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

    middle_name: str | None = Field(
        default=None,
        title="Middle Name",
        description="Middle name(s) of the User",
        max_length=50,
    )
    gender: Gender | None = Field(
        default=None, title="Gender", description="Gender of the User"
    )
    birthdate: date | None = Field(
        default=None, title="Birthdate", description="Birthday of the User"
    )
    phone_number: PhoneNumber | None = Field(
        default=None,
        title="Phone number",
        description="Preferred telephone number of the User",
    )
    address: Address | None = Field(
        default=None, title="Address", description="Address of the User"
    )

    @field_validator("phone_number", mode="before")
    def validate_phone_number(cls, v: PhoneNumber | None) -> PhoneNumber | None:
        """
        Validates the phone number attribute
        :param v: The phone number value to validate
        :type v: Optional[PhoneNumber]
        :return: The validated phone number
        :rtype: Optional[PhoneNumber]
        """
        return validate_phone_number(v)


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
