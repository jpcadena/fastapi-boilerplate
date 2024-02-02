"""
A module for address in the app-schemas package.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, UUID4

from app.config.config import init_setting, sql_database_setting
from app.schemas.schemas import (
    address_response_example,
    address_update_example,
    common_address_data,
    id_example,
    updated_at_example,
    user_address_in_db_example,
)


class AddressID(BaseModel):
    """
    Schema for representing an Address's ID.
    """

    model_config = ConfigDict(json_schema_extra=id_example)

    id: UUID4 = Field(
        default_factory=UUID4, title="ID", description="ID of the Address"
    )


class AddressUpdatedAt(BaseModel):
    """
    Schema for representing the update timestamp of an Address.
    """

    model_config = ConfigDict(
        json_schema_extra=updated_at_example,
    )

    updated_at: datetime | None = Field(
        default=None,
        title="Updated at",
        description="Time the Address was updated",
    )


class AddressUpdate(BaseModel):
    """
    Schema for the Address of a User.
    """

    model_config = ConfigDict(
        json_schema_extra=address_update_example,
    )

    street_address: str = Field(
        ...,
        title="Street Address",
        description="Full street address component, which may include house"
        " number, street name, Post Office Box, and multi-line"
        " extended street address information. This field ma"
        "y contain multiple lines, separated by newlines.",
        min_length=3,
    )
    locality: str = Field(
        ...,
        title="Locality (City)",
        description="City or locality component.",
        min_length=3,
        max_length=85,
    )


class AddressResponse(AddressUpdate):
    """
    Schema for representing the Address of a User.
    """

    model_config = ConfigDict(
        json_schema_extra=address_response_example,
    )

    region: str = Field(
        default=init_setting.DEFAULT_REGION,
        title="Region (State/Province)",
        description="State, province, prefecture, or region component.",
        min_length=4,
        max_length=35,
    )
    country: str = Field(
        default=init_setting.DEFAULT_COUNTRY,
        title="Country",
        description="Country name component.",
        min_length=4,
        max_length=60,
    )


class Address(AddressResponse):
    """
    Schema for representing the Address for JWT.
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra=common_address_data,
    )

    postal_code: str | None = Field(
        None,
        title="Postal Code",
        min_length=6,
        max_length=6,
        pattern=sql_database_setting.DB_POSTAL_CODE_CONSTRAINT,
        description="Postal code should be a 6-digit number.",
    )


class UserAddressInDB(AddressID, Address, AddressUpdatedAt):
    """
    Schema for updating the Address of a User.
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra=user_address_in_db_example,
    )

    created_at: datetime = Field(
        default_factory=datetime.now,
        title="Created at",
        description="Time the User was created",
    )
