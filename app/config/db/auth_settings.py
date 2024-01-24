"""
A module for auth settings in the app.core.config package.
"""
from typing import Optional

from pydantic import AnyHttpUrl, PositiveInt, RedisDsn, field_validator
from pydantic_core import Url
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    """
    Settings class for authentication using JWT and Redis
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )

    MAX_REQUESTS: PositiveInt = 30
    RATE_LIMIT_DURATION: PositiveInt = 60
    BLACKLIST_EXPIRATION_SECONDS: PositiveInt = 3600
    API_V1_STR: str = "/api/v1"
    ALGORITHM: str = "HS256"
    AUTH_URL: str = "api/v1/auth/"
    TOKEN_URL: str = "api/v1/auth/login"
    OAUTH2_SCHEME: str = "JWT"
    OAUTH2_TOKEN_DESCRIPTION: str = (
        "JWT token used to authenticate most of" " the API endpoints."
    )
    OAUTH2_REFRESH_TOKEN_DESCRIPTION: str = (
        "JWT token used to authenticate" " most of he API endpoints."
    )
    TOKEN_USER_INFO_REGEX: str = (
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
        r"[0-9a-f]{4}-[0-9a-f]{12}:\d{1,3}\."
        r"\d{1,3}\.\d{1,3}\.\d{1,3}$"
    )
    SUB_REGEX: str = (
        r"^username:[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-"
        r"[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    )
    HEADERS: dict[str, str] = {"WWW-Authenticate": "Bearer"}
    DETAIL: str = "Could not validate credentials"
    NO_CLIENT_FOUND: str = "No client found on the request"
    SECRET_KEY: str
    SERVER_URL: AnyHttpUrl
    SERVER_DESCRIPTION: str
    CACHE_SECONDS: PositiveInt = 3600
    ACCESS_TOKEN_EXPIRE_MINUTES: float
    REFRESH_TOKEN_EXPIRE_MINUTES: PositiveInt
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: PositiveInt
    AUDIENCE: Optional[AnyHttpUrl] = None
    STRICT_TRANSPORT_SECURITY_MAX_AGE: PositiveInt

    @field_validator("AUDIENCE", mode="before")
    def assemble_audience(
        cls, v: Optional[str], info: ValidationInfo  # noqa: argument-unused
    ) -> AnyHttpUrl:
        """
        Combine server host and API_V1_STR to create the audience
        string.
        :param v: The value of audience attribute
        :type v: Optional[str]
        :param info: The field validation info
        :type info: ValidationInfo
        :return: The AUDIENCE attribute
        :rtype: AnyHttpUrl
        """
        if info.config is None:
            raise ValueError("info.config cannot be None")
        return AnyHttpUrl(
            f'{str(info.data.get("SERVER_URL"))[:-1]}:8000/'
            f'{info.data.get("TOKEN_URL")}'
        )

    REDIS_SCHEME: str
    REDIS_HOST: str
    REDIS_USERNAME: str
    REDIS_PASSWORD: str
    REDIS_PORT: PositiveInt
    REDIS_DATABASE_URI: Optional[RedisDsn] = None

    @field_validator("REDIS_DATABASE_URI", mode="before")
    def assemble_redis_connection(
        cls, v: Optional[str], info: ValidationInfo  # noqa: argument-unused
    ) -> RedisDsn:
        """
        Assemble the cache database connection as URI string
        :param v: Variables to consider
        :type v: str
        :param info: The field validation info
        :type info: ValidationInfo
        :return: Redis URI
        :rtype: RedisDsn
        """
        if info.config is None:
            raise ValueError("info.config cannot be None")
        return RedisDsn(
            str(
                Url.build(
                    scheme=info.data.get("REDIS_SCHEME", ""),
                    username=info.data.get("REDIS_USERNAME"),
                    password=info.data.get("REDIS_PASSWORD"),
                    host=info.data.get("REDIS_HOST", ""),
                    port=info.data.get("REDIS_PORT"),
                )
            )
        )
