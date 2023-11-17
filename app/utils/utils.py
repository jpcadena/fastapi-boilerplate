"""
A module for utils in the app.utils package.
"""
import logging
import math
import re
from typing import Any, Optional

import phonenumbers
import pycountry
from fastapi import Depends
from pydantic import EmailStr, PositiveInt
from pydantic_extra_types.phone_numbers import PhoneNumber

from app.config.config import get_init_settings, sql_database_setting
from app.config.init_settings import InitSettings
from app.exceptions.exceptions import ServiceException
from app.utils.files_utils.json_utils import read_json_file, write_json_file
from app.utils.files_utils.openapi_utils import modify_json_data

logger: logging.Logger = logging.getLogger(__name__)


async def update_json(
    init_setting: InitSettings = Depends(get_init_settings),
) -> None:
    """
    Update JSON file for client
    :param init_setting: Dependency method for cached setting object
    :type init_setting: InitSettings
    :return: None
    :rtype: NoneType
    """
    data: dict[str, Any] = await read_json_file(init_setting)
    data = modify_json_data(data)
    await write_json_file(data, init_setting)
    logger.info("Updated OpenAPI JSON file")


def hide_email(email: EmailStr) -> str:
    """
    Hide email using **** for some characters
    :param email: Email address to hide some values
    :type email: EmailStr
    :return: Email address with some **** for its value
    :rtype: str
    """
    email_title, email_domain = email.split("@")
    title_count: PositiveInt = max(math.ceil(len(email_title) / 2), 1)
    domain_sections = email_domain.split(".")
    domain_first_section = domain_sections[0]
    domain_count: PositiveInt = max(math.ceil(len(domain_first_section) / 2), 1)
    replaced_title: str = email_title.replace(
        email_title[title_count * -1 :], "*" * title_count
    )
    replaced_domain_first: str = domain_first_section.replace(
        domain_first_section[domain_count * -1 :], "*" * domain_count
    )
    replaced_domain: str = (
        replaced_domain_first + "." + ".".join(domain_sections[1:])
    )
    hidden_email: str = f"{replaced_title}@{replaced_domain}"
    return hidden_email


def get_nationality_code(country_name: str) -> str:
    """
    Get the nationality code given a country name
    :param country_name: The name of the country
    :type country_name: str
    :return: The nationality in ICAO 3-letter code [ICAO-Doc9303]
    :rtype: str
    """
    try:
        country = pycountry.countries.get(name=country_name)
        if country:
            return str(country.alpha_3)
    except LookupError:
        pass
    return ""


def validate_phone_number(phone_number: PhoneNumber) -> PhoneNumber:
    """
    Validate the phone number format
    :param phone_number: The phone number to validate
    :type phone_number: str
    :return: The validated phone number
    :rtype: str
    """
    try:
        parsed_number = phonenumbers.parse(phone_number, None)
    except phonenumbers.phonenumberutil.NumberParseException as exc:
        raise ValueError from exc
    if not phonenumbers.is_valid_number(parsed_number):
        raise ValueError("Invalid phone number")
    return phone_number


def validate_password(password: Optional[str]) -> str:
    """
    Validates a password based on given criteria.
    :param password: The password to validate.
    :type password: Optional[str]
    :return: The validated password.
    :rtype: str
    """
    if not password:
        raise ServiceException("Password is empty")
    if not (
        re.search("[A-Z]", password)
        and re.search("[a-z]", password)
        and re.search("[0-9]", password)
        and re.search(
            sql_database_setting.DB_USER_PASSWORD_CONSTRAINT, password
        )
        and 8 <= len(password) <= 14
    ):
        raise ValueError("Password validation failed")
    return password
