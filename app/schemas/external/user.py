"""
A module for user schema in the app schemas package.
"""
from datetime import date, datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import (
    UUID4,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)
from pydantic_extra_types.phone_numbers import PhoneNumber

from app.config.config import init_setting
from app.schemas.external.address import Address, AddressUpdate
from app.schemas.infrastructure.gender import Gender
from app.utils.utils import validate_password


class UserID(BaseModel):
    """
    Schema for representing a User's ID.
    """

    id: UUID4 = Field(
        default_factory=UUID4, title="ID", description="ID of the User"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": str(uuid4()),
            }
        },
    )


class UserUpdatedAt(BaseModel):
    """
    Schema for representing the update timestamp of a User.
    """

    updated_at: Optional[datetime] = Field(
        default=None,
        title="Updated at",
        description="Time the User was updated",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "updated_at": str(datetime.now()),
            }
        },
    )


class UserBaseAuth(BaseModel):
    """
    Schema for representing the basic authentication attributes of a
     User.
    """

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

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "username",
                "email": "example@mail.com",
            }
        },
    )


class UserFilter(UserBaseAuth, UserID):
    """
    Schema for filtering User records.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": str(uuid4()),
                "username": "username",
                "email": "example@mail.com",
            }
        },
    )


class UserName(BaseModel):
    """
    Schema for representing the name attributes of a User.
    """

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

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "first_name": "Some",
                "last_name": "Example",
            }
        },
    )


class UserBase(UserName, UserBaseAuth):
    """
    Base schema for representing a User.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "username",
                "email": "example@mail.com",
                "first_name": "Some",
                "last_name": "Example",
            }
        },
    )


class UserAuth(UserBaseAuth, UserID):
    """
    User Auth that inherits from UserID.
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": str(uuid4()),
                "username": "username",
                "email": "example@mail.com",
            }
        },
    )


class UserOptional(BaseModel):
    """
    Schema for representing a User with optional attributes.
    """

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

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "middle_name": "One",
                "gender": Gender.MALE,
                "birthdate": str(date(2004, 1, 1)),
                "phone_number": PhoneNumber("+593987654321"),
                "address": AddressUpdate(
                    street_address="Urdesa Norte mz A1 v 99",
                    locality="Guayaquil",
                ).model_dump(),
            }
        },
    )


class UserCreate(UserOptional, UserBase):
    """
    Schema for creating a User record.
    """

    password: str = Field(
        ...,
        title="Password",
        description="Password of the User",
        min_length=8,
        max_length=14,
    )

    # email_encrypted_info: str = Field(
    #     ..., title="Email encrypted info",
    #     description="The encrypted information for the user's email address"
    # )
    # phone_number_encrypted_info: str = Field(
    #     ..., title="Phone number info",
    #     description="The encrypted information for the user's phone number"
    # )
    # birthdate_encrypted_info: str = Field(
    #     ..., title="Birthdate encrypted info",
    #     description="The encrypted information for the user's birthdate"
    # )

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

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "username": "username",
                "email": "example@mail.com",
                "first_name": "Some",
                "last_name": "Example",
                "middle_name": "One",
                "password": "Hk7pH9*35Fu&3U",
                "gender": Gender.MALE,
                "birthdate": str(date(2004, 12, 31)),
                "phone_number": PhoneNumber("+593987654321"),
                "address": Address(
                    street_address="Urdesa Norte mz A1 v 99",
                    locality="Guayaquil",
                    region=init_setting.DEFAULT_REGION,
                    country=init_setting.DEFAULT_COUNTRY,
                    postal_code="090505",
                ).model_dump(),
            }
        },
    )


class UserSuperCreate(UserCreate):
    """
    Schema for creating a superuser.
    """

    is_superuser: bool = Field(
        default=True,
        title="Is super user?",
        description="True if the user is super user; otherwise false",
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "username": "username",
                "email": "example@mail.com",
                "first_name": "Some",
                "last_name": "Example",
                "middle_name": "One",
                "password": "Hk7pH9*35Fu&3U",
                "gender": Gender.MALE,
                "birthdate": str(date(2004, 12, 31)),
                "phone_number": PhoneNumber("+593987654321"),
                "address": Address(
                    street_address="Urdesa Norte mz A1 v 99",
                    locality="Guayaquil",
                    region=init_setting.DEFAULT_REGION,
                    country=init_setting.DEFAULT_COUNTRY,
                    postal_code="090505",
                ).model_dump(),
                "is_superuser": True,
            }
        },
    )


class UserCreateResponse(UserBase, UserID):
    """
    Schema for the response when creating a User.
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": str(uuid4()),
                "username": "username",
                "email": "example@mail.com",
                "first_name": "Some",
                "last_name": "Example",
            }
        },
    )


class UserUpdate(BaseModel):
    """
    Schema for updating a User record.
    """

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

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "username": "username",
                "email": "example@mail.com",
                "first_name": "Some",
                "middle_name": "One",
                "last_name": "Example",
                "password": "Hk7pH9*35Fu&3U",
                "gender": Gender.MALE,
                "birthdate": str(date(2004, 12, 31)),
                "phone_number": PhoneNumber("+593987654321"),
                "address": AddressUpdate(
                    street_address="Urdesa Norte mz A1 v 99",
                    locality="Guayaquil",
                ).model_dump(),
            }
        },
    )


class UserInDB(UserUpdatedAt, BaseModel):
    """
    Schema for representing a User record in the database.
    """

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

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "is_active": True,
                "is_superuser": False,
                "created_at": str(datetime.now()),
                "updated_at": str(datetime.now()),
            }
        },
    )


class UserPassword(BaseModel):
    """
    Schema for representing a User's password.
    """

    password: str = Field(
        ...,
        title="Hashed Password",
        description="Hashed Password of the User",
        min_length=60,
        max_length=60,
    )
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "password": "Hk7pH9*Hk7pH9*35Fu&3UHk7pH9*35Fu&3U35Fu&3U",
            }
        },
    )


class UserUpdateResponse(
    UserInDB, UserOptional, UserPassword, UserName, UserAuth
):
    """
    Schema for the response when updating a User.
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": str(uuid4()),
                "username": "username",
                "email": "example@mail.com",
                "first_name": "Some",
                "last_name": "Example",
                "middle_name": "One",
                "password": "Hk7pH9*Hk7pH9*35Fu&3UHk7pH9*35Fu&3U35Fu&3U",
                "gender": Gender.MALE,
                "birthdate": str(date(2004, 12, 31)),
                "phone_number": PhoneNumber("+593987654321"),
                "address_id": str(uuid4()),
                "address": AddressUpdate(
                    street_address="Urdesa Norte mz A1 v 99",
                    locality="Guayaquil",
                ).model_dump(),
                "is_active": True,
                "is_superuser": False,
                "created_at": (str(datetime.now())),
                "updated_at": str(datetime.now()),
            }
        },
    )


class User(UserUpdatedAt, UserOptional, UserBase):
    """
    Schema for representing a User.
    """

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

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": str(uuid4()),
                "username": "username",
                "email": "example@mail.com",
                "first_name": "Some",
                "last_name": "Example",
                "middle_name": "One",
                "password": "Hk7pH9*Hk7pH9*35Fu&3UHk7pH9*35Fu&3U35Fu&3U",
                "gender": Gender.MALE,
                "birthdate": str(date(2004, 12, 31)),
                "phone_number": PhoneNumber("+593987654321"),
                "address_id": str(uuid4()),
                "address": Address(
                    street_address="Urdesa Norte mz A1 v 99",
                    locality="Guayaquil",
                    region=init_setting.DEFAULT_REGION,
                    country=init_setting.DEFAULT_COUNTRY,
                    postal_code="090505",
                ).model_dump(),
                "is_active": True,
                "is_superuser": False,
                "created_at": str(datetime.now()),
                "updated_at": str(datetime.now()),
            }
        },
    )


class UserResponse(UserInDB, UserOptional, UserBase, UserID):
    """
    Schema for the response when retrieving a User.
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": str(uuid4()),
                "username": "username",
                "email": "example@mail.com",
                "first_name": "Some",
                "last_name": "Example",
                "middle_name": "One",
                "gender": Gender.MALE,
                "birthdate": str(date(2004, 12, 31)),
                "phone_number": PhoneNumber("+593987654321"),
                "address_id": str(uuid4()),
                "address": Address(
                    street_address="Urdesa Norte mz A1 v 99",
                    locality="Guayaquil",
                    region=init_setting.DEFAULT_REGION,
                    country=init_setting.DEFAULT_COUNTRY,
                    postal_code="090505",
                ).model_dump(),
                "is_active": True,
                "is_superuser": False,
                "created_at": str(datetime.now()),
                "updated_at": str(datetime.now()),
            }
        },
    )


def custom_serializer(my_dict: dict[str, Any]) -> dict[str, Any]:
    """
    Custom serializer for User model
    :param my_dict: The dictionary representation of the User model object
    :type my_dict: dict[str, Any]
    :return: The serialized dictionary
    :rtype: dict[str, Any]
    """
    for key, value in my_dict.items():
        if isinstance(value, UUID):
            my_dict[key] = str(value)
        elif isinstance(value, Enum):
            my_dict[key] = value.value
        elif isinstance(value, datetime):
            my_dict[key] = value.isoformat()
        elif isinstance(value, dict):
            custom_serializer(value)
    return my_dict
