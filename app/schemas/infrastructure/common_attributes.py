"""
A module for common attributes between User and Token in the app-schemas
package.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, PastDate
from pydantic_extra_types.phone_numbers import PhoneNumber

from app.schemas.external.address import Address
from app.schemas.infrastructure.gender import Gender
from app.schemas.schemas import common_user_token_example, editable_data_example


class EditableData(BaseModel):
    """
    Editable fields for User and Token classes based on Pydantic
     Base Model.
    """

    model_config = ConfigDict(
        json_schema_extra=editable_data_example,
    )

    phone_number: Optional[PhoneNumber] = Field(
        default=None,
        title="Telephone",
        description="Preferred telephone number of the User",
        validate_default=True,
    )
    address: Address = Field(
        default=...,
        title="Address",
        description="Preferred postal address of the User",
    )


class CommonUserToken(EditableData):
    """
    Common fields for User and Token classes based on EditableData.
    """

    model_config = ConfigDict(
        json_schema_extra=common_user_token_example,
    )

    given_name: str = Field(
        ...,
        title="First name",
        description="Given name(s) or first name(s) of the User",
        min_length=1,
        max_length=50,
    )
    family_name: str = Field(
        ...,
        title="Last name",
        description="Surname(s) or last name(s) of the User",
        min_length=1,
        max_length=50,
    )
    middle_name: Optional[str] = Field(
        ...,
        title="Middle name",
        description="Middle name(s) of the User",
        max_length=50,
    )
    gender: Optional[Gender] = Field(
        default=Gender.MALE, title="Gender", description="Gender of the User"
    )
    birthdate: Optional[PastDate] = Field(
        default=None, title="Birthdate", description="Birthday of the User"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        title="Updated at",
        description="Time the User information was last updated",
    )
