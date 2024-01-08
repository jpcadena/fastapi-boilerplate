"""
A module for token in the app-schemas package.
"""
import re
from typing import Literal, Optional
from uuid import uuid4

from pydantic import (
    UUID4,
    AnyHttpUrl,
    AnyUrl,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    NonNegativeInt,
    field_validator,
)

from app.config.config import auth_setting
from app.exceptions.exceptions import ServiceException
from app.schemas.infrastructure.common_attributes import CommonUserToken
from app.schemas.infrastructure.http_method import HttpMethod
from app.schemas.infrastructure.scope import Scope
from app.schemas.schemas import (
    public_claims_token_example,
    registered_claims_token_example,
    token_example,
    token_payload_example,
    token_response_example,
)
from app.utils.utils import validate_password


class PublicClaimsToken(CommonUserToken):
    """
    Token class based on Pydantic Base Model with Public claims (IANA).
    """

    model_config = ConfigDict(
        json_schema_extra=public_claims_token_example,
    )

    email: EmailStr = Field(
        ...,
        title="Email",
        description="Preferred e-mail address of the User",
    )
    nickname: str = Field(
        ...,
        title="Casual name",
        description="Casual name of the User (First Name)",
        min_length=1,
        max_length=50,
    )
    preferred_username: str = Field(
        ...,
        title="Preferred username",
        description="Shorthand name by which the End-User wishes to be "
        "referred to (Username)",
        min_length=1,
        max_length=50,
    )


class RegisteredClaimsToken(BaseModel):
    """
    Registered Claims Token class based on Pydantic Base Model with
    Registered claims.
    """

    model_config = ConfigDict(
        json_schema_extra=registered_claims_token_example,
    )

    iss: Optional[AnyUrl] = Field(
        default=auth_setting.SERVER_URL,
        title="Issuer",
        description="Principal that issued JWT as HTTP URL",
    )
    sub: str = Field(
        ...,
        title="Subject",
        description="Subject of JWT starting with username: followed"
        " by User ID",
        validate_default=True,
        min_length=45,
        max_length=45,
    )
    aud: Optional[str] = Field(
        default=auth_setting.AUDIENCE.__str__(),
        title="Audience",
        description="Recipient of JWT",
        min_length=1,
    )
    exp: NonNegativeInt = Field(
        ...,
        title="Expiration time",
        description="Expiration time on or after which the JWT MUST NOT be"
        " accepted for processing",
    )
    nbf: NonNegativeInt = Field(
        ...,
        title="Not Before",
        description="Time Before which the JWT MUST NOT be accepted for "
        "processing",
    )
    iat: NonNegativeInt = Field(
        ..., title="Issued At", description="Time at which the JWT was issued"
    )
    jti: Optional[UUID4] = Field(
        default_factory=uuid4,
        title="JWT ID",
        description="Unique Identifier for the JWT",
    )
    sid: Optional[UUID4] = Field(
        default_factory=uuid4,
        title="Session ID",
        description="Session ID",
    )
    scope: Optional[Scope] = Field(
        default=Scope.ACCESS_TOKEN, title="Scope", description="Scope value"
    )
    at_use_nbr: int = Field(
        default=auth_setting.MAX_REQUESTS,
        title="Number of requests",
        description="Number of API requests for which the access token can be"
        " used",
        gt=0,
        le=30,
    )
    nationalities: Optional[list[str]] = Field(
        default=["ECU"],
        title="Nationalities",
        description="String array representing the End-User's nationalities",
        min_length=1,
        max_length=200,
    )
    htm: Optional[Literal[HttpMethod.POST]] = HttpMethod.POST
    htu: Optional[AnyHttpUrl] = Field(
        default=AnyHttpUrl(
            f"{auth_setting.SERVER_URL.__str__()}{auth_setting.TOKEN_URL}",
        ),
        title="HTTP URI",
        description="The HTTP URI of the request",
    )

    @field_validator("sub", mode="before")
    def username_starts_with_non_zero(cls, v: Optional[str]) -> str:
        """
        Validate that the username starts with a non-zero
        :param v: The sub value
        :type v: Optional[str]
        :return: The validated sub attribute
        :rtype: str
        """
        # pylint: disable=no-self-argument
        if not v:
            raise ServiceException("sub is empty")
        if re.match(auth_setting.SUB_REGEX, v):
            return v
        raise ValueError(
            "sub must start with 'username:' followed by non-zero digits"
        )


class TokenPayload(PublicClaimsToken, RegisteredClaimsToken):
    """
    Token Payload class based on RegisteredClaimsToken and PublicClaimsToken.
    """

    model_config = ConfigDict(
        json_schema_extra=token_payload_example,
    )


class Token(BaseModel):
    """
    Token that inherits from Pydantic Base Model.
    """

    model_config = ConfigDict(
        json_schema_extra=token_example,
    )

    access_token: str = Field(
        ..., title="Token", description="Access token", min_length=30
    )
    refresh_token: str = Field(
        ..., title="Refresh Token", description="Refresh token", min_length=30
    )


class TokenResponse(Token):
    """
    Token for Response based on Pydantic Base Model.
    """

    model_config = ConfigDict(
        json_schema_extra=token_response_example,
    )

    token_type: str = Field(
        default="bearer", title="Token type", description="Type of the token"
    )


class TokenResetPassword(BaseModel):
    """
    Token Reset Password for Request based on Pydantic Base Model.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
                "password": "Hk7pH9*35Fu&3U",
            }
        }
    )

    token: str = Field(
        ..., title="Token", description="Access token", min_length=30
    )
    password: str = Field(
        ...,
        title="New password",
        description="New password to reset",
        validate_default=True,
        min_length=8,
        max_length=14,
    )

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
