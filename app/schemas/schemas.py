"""
A module for schemas in the app-schemas package.
"""
from datetime import date, datetime
from enum import Enum
from typing import Any, cast
from uuid import UUID, uuid4

from pydantic.config import JsonDict
from pydantic_extra_types.phone_numbers import PhoneNumber

from app.config.config import auth_setting, init_setting
from app.schemas.infrastructure.gender import Gender
from app.schemas.infrastructure.http_method import HttpMethod
from app.schemas.infrastructure.scope import Scope

# Centralized common example data
common_address_data: JsonDict = {
    "street_address": "Blvd 9 de Octubre",
    "locality": "Guayaquil",
    "region": init_setting.DEFAULT_REGION,
    "country": init_setting.DEFAULT_COUNTRY,
    "postal_code": "090312",
}

common_user_data: JsonDict = {
    "username": "username",
    "email": "example@mail.com",
    "first_name": "Some",
    "last_name": "Example",
    "middle_name": "One",
    "gender": Gender.MALE,
    "birthdate": date(2004, 1, 1).strftime(init_setting.DATE_FORMAT),
    "phone_number": str(PhoneNumber("+593987654321")),
}

# Fixed timestamp and UUID for consistency
fixed_timestamp: str = datetime.now().strftime(init_setting.DATETIME_FORMAT)
fixed_uuid: str = str(uuid4())


def merge_examples(*examples: Any) -> JsonDict:
    """
    Helper function to merge examples
    :param examples:
    :type examples:
    :return:
    :rtype:
    """
    merged_example: JsonDict = {}
    for example in examples:
        merged_example.update(cast(JsonDict, example))
    return {"example": merged_example}


# Creating examples using the helper function and common data
id_example: JsonDict = {"example": {"id": fixed_uuid}}

address_update_example: JsonDict = {"example": common_address_data}

address_response_example: JsonDict = merge_examples(
    address_update_example["example"],
    {"postal_code": common_address_data["postal_code"]},
)

updated_at_example: JsonDict = {"example": {"updated_at": fixed_timestamp}}

user_address_in_db_example: JsonDict = merge_examples(
    id_example["example"],
    address_response_example["example"],
    updated_at_example["example"],
)

token_example: JsonDict = {
    "example": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
    }
}

token_response_example: JsonDict = merge_examples(
    token_example["example"], {"token_type": "bearer"}
)

user_base_auth_example: JsonDict = {"example": common_user_data}

updated_user_base_auth_example: JsonDict = common_user_data.copy()
updated_user_base_auth_example.pop("first_name")
updated_user_base_auth_example.pop("last_name")
updated_user_base_auth_example.pop("middle_name")
updated_user_base_auth_example.pop("gender")
updated_user_base_auth_example.pop("birthdate")
updated_user_base_auth_example.pop("phone_number")


user_auth_example: JsonDict = merge_examples(
    id_example["example"], updated_user_base_auth_example
)

username_example: JsonDict = {
    "example": {
        "first_name": "Some",
        "last_name": "Example",
    }
}

user_base_example: JsonDict = merge_examples(
    user_base_auth_example["example"], username_example["example"]
)

user_optional_example: JsonDict = {
    "example": {
        "middle_name": "One",
        "gender": Gender.MALE,
        "birthdate": date(2004, 1, 1).strftime(init_setting.DATE_FORMAT),
        "phone_number": PhoneNumber("+593987654321"),
        "address": address_response_example["example"],
    }
}

user_create_example: JsonDict = merge_examples(
    user_base_example["example"],
    user_optional_example["example"],
    {"password": "Hk7pH9*35Fu&3U"},
)

user_super_create_example: JsonDict = merge_examples(
    user_create_example["example"], {"is_superuser": True}
)

user_create_response_example: JsonDict = merge_examples(
    id_example["example"], user_base_example["example"]
)

user_update_example: JsonDict = user_create_example

user_in_db_example: JsonDict = merge_examples(
    {"is_active": True, "is_superuser": False, "created_at": fixed_timestamp},
    updated_at_example["example"],
)

user_password_example: JsonDict = {
    "example": {
        "password": "Hk7pH9*Hk7pH9*35Fu&3UHk7pH9*35Fu&3U35Fu&3U",
    }
}

user_update_response_example: JsonDict = merge_examples(
    user_auth_example["example"],
    username_example["example"],
    user_password_example["example"],
    user_optional_example["example"],
    {"address_id": fixed_uuid},
    user_in_db_example["example"],
)

user_example: JsonDict = user_update_response_example

user_response_example: JsonDict = merge_examples(
    user_create_response_example["example"],
    user_optional_example["example"],
    {"address_id": fixed_uuid},
    user_in_db_example["example"],
)

updated_common_user_data: JsonDict = common_user_data.copy()
updated_common_user_data["nickname"] = updated_common_user_data.pop("username")
updated_common_user_data["given_name"] = updated_common_user_data.pop(
    "first_name"
)
updated_common_user_data["family_name"] = updated_common_user_data.pop(
    "last_name"
)
updated_common_user_data["preferred_name"] = updated_common_user_data[
    "nickname"
]

public_claims_token_example: JsonDict = merge_examples(
    updated_common_user_data,
    updated_at_example["example"],
    common_address_data,
)

registered_claims_token_example: JsonDict = {
    "example": {
        "iss": f"{auth_setting.SERVER_URL}",
        "sub": "username:c3ee0ef6-3a18-4251-af6d-138a8c8fec25",
        "aud": f"{auth_setting.SERVER_URL}:80" f"/{auth_setting.TOKEN_URL}",
        "exp": 1672433102,
        "nbf": 1672413301,
        "iat": 1672413302,
        "jti": str(uuid4()),
        "sid": str(uuid4()),
        "scope": f"{Scope.ACCESS_TOKEN}",
        "at_use_nbr": 1,
        "nationalities": ["ECU"],
        "htm": f"{HttpMethod.POST}",
        "htu": f"{auth_setting.AUDIENCE}",
    }
}

token_payload_example: JsonDict = merge_examples(
    public_claims_token_example["example"],
    registered_claims_token_example["example"],
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
