"""
A module for settings in the app.core.config package.
"""

import os
from typing import Any

from pydantic import (
    AnyHttpUrl,
    EmailStr,
    FilePath,
    IPvAnyAddress,
    PositiveInt,
    field_validator,
)
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings class based on Pydantic Base Settings
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )

    SERVER_HOST: IPvAnyAddress
    SERVER_PORT: PositiveInt
    SERVER_RELOAD: bool
    SERVER_LOG_LEVEL: str
    SMTP_PORT: PositiveInt
    SMTP_HOST: str
    SMTP_USER: str
    SMTP_PASSWORD: str
    MAIL_SUBJECT: str
    MAIL_TIMEOUT: float
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: str | None = None
    SUPERUSER_EMAIL: EmailStr
    SUPERUSER_FIRST_NAME: str
    SUPERUSER_PASSWORD: str
    SUPERUSER_LAST_NAME: str
    SUPERUSER_STREET_ADDRESS: str
    SUPERUSER_LOCALITY: str
    SUPERUSER_POSTAL_CODE: str
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    PUBLIC_KEY_PATH: FilePath
    PRIVATE_KEY_PATH: FilePath

    @field_validator(
        "PUBLIC_KEY_PATH", "PRIVATE_KEY_PATH", mode="before", check_fields=True
    )
    def validate_key_paths(cls, key_path: FilePath) -> FilePath:
        """
        Validate the provided key path.
        :param key_path: Provided key path
        :type key_path: FilePath
        :return: The validated key path
        :rtype: FilePath
        """
        if not str(key_path).endswith(".pem"):
            raise ValueError(f"{key_path} must have a .pem extension")
        base_name: str = os.path.basename(key_path)
        if not base_name.endswith("key.pem"):
            raise ValueError(
                f"{key_path} must have a file name ending with 'key'"
            )
        return key_path

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        """
        Assemble a list of allowed CORS origins.
        :param v: Provided CORS origins, either a string or a list of
        strings
        :type v: Union[str, list[str]]
        :return: List of Backend CORS origins to be accepted
        :rtype: Union[list[str], str]
        """
        # pylint: disable=unused-argument,no-self-argument,invalid-name
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        if isinstance(v, list):
            return v
        raise ValueError(v)

    CONTACT_NAME: str | None = None
    CONTACT_URL: AnyHttpUrl | None = None
    CONTACT_EMAIL: EmailStr | None = None
    CONTACT: dict[str, Any] | None = None

    @field_validator("CONTACT", mode="before")
    def assemble_contact(
            cls, v: str | None, info: ValidationInfo  # noqa: argument-unused
    ) -> dict[str, str]:
        """
        Assemble contact information
        :param v: Variables to consider
        :type v: str
        :param info: The field validation info
        :type info: ValidationInfo
        :return: The contact attribute
        :rtype: dict[str, str]
        """
        if info.config is None:
            raise ValueError("info.config cannot be None")
        contact: dict[str, Any] = {}
        if info.data.get("CONTACT_NAME"):
            contact["name"] = info.data.get("CONTACT_NAME")
        if info.data.get("CONTACT_URL"):
            contact["url"] = info.data.get("CONTACT_URL")
        if info.data.get("CONTACT_EMAIL"):
            contact["email"] = info.data.get("CONTACT_EMAIL")
        return contact
