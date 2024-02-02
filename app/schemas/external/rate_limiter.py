"""
A module for rate limiter in the app.schemas.external package.
"""

from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress

from app.schemas.schemas import rate_limiter_example, raw_rate_limiter_example


class RateLimiter(BaseModel):
    """
    The rate limiter model inherited from Pydantic Base Model
    """

    model_config = ConfigDict(json_schema_extra=rate_limiter_example)

    ip_address: IPvAnyAddress = Field(
        ...,
        title="IP Address",
        description="The IP address of the client making the request.",
        examples=[raw_rate_limiter_example["ip_address"]],
    )
    user_agent: str = Field(
        ...,
        title="User Agent",
        description="The user-agent string from the client's request header,"
        " representing the client's browser or other client"
        " application.",
        examples=[raw_rate_limiter_example["user_agent"]],
    )
    request_path: str = Field(
        ...,
        title="Request path",
        description="The path or endpoint the client is trying to access on"
        " the server.",
        examples=[raw_rate_limiter_example["request_path"]],
    )
