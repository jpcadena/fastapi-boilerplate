"""
A module for utils in the app.utils package.
"""
import contextlib
import logging
import math
import re
from ipaddress import AddressValueError, IPv4Address, IPv6Address, ip_address
from typing import Annotated, Any, Optional, Union

import phonenumbers
import pycountry
from fastapi import Depends, Request
from pydantic import EmailStr, PositiveInt
from pydantic_extra_types.phone_numbers import PhoneNumber
from starlette.datastructures import Address

from app.config.config import get_init_settings, sql_database_setting
from app.config.init_settings import InitSettings
from app.exceptions.exceptions import NotFoundException, ServiceException
from app.utils.files_utils.json_utils import (
    get_json_file_path,
    read_json_file,
    write_json_file,
)
from app.utils.files_utils.openapi_utils import modify_json_data

logger: logging.Logger = logging.getLogger(__name__)


async def update_json(
    init_settings: Annotated[InitSettings, Depends(get_init_settings)],
) -> None:
    """
    Update JSON file for client
    :param init_settings: Dependency method for cached setting object
    :type init_settings: InitSettings
    :return: None
    :rtype: NoneType
    """
    file_path: str = get_json_file_path(init_settings)
    data: dict[str, Any] = await read_json_file(
        file_path, init_settings.ENCODING
    )
    data = modify_json_data(data)
    await write_json_file(data, file_path, init_settings.ENCODING)
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
    replaced_domain: str = f"{replaced_domain_first}." + ".".join(
        domain_sections[1:]
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
    with contextlib.suppress(LookupError):
        if country := pycountry.countries.get(name=country_name):
            return str(country.alpha_3)
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


def get_client_ip(request: Request) -> Union[IPv4Address, IPv6Address]:
    """
    Extract the client IP address from the request.
    :param request: The FastAPI request object.
    :type request: Request
    :return: The extracted IP address.
    :rtype: Union[IPv4Address, IPv6Address]
    """
    client: Optional[Address] = request.client
    if not client:
        raise NotFoundException("No client found on the request")
    client_ip: str = client.host
    try:
        return ip_address(client_ip)
    except AddressValueError as exc:
        raise ValueError("Invalid IP address in the request.") from exc
