"""
A module for rate limiter in the app.schemas.external package.
"""

from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress


class RateLimiter(BaseModel):
    """
    The rate limiter model inherited from Pydantic Base Model
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ip_address": "127.0.0.1",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                " AppleWebKit/537.36 (KHTML, like Gecko)"
                " Chrome/58.0.3029.110 Safari/537.3",
                "request_path": "/api/v1/data",
            }
        }
    )

    ip_address: IPvAnyAddress = Field(
        ...,
        title="IP Address",
        description="The IP address of the client making the request.",
        examples=["127.0.0.1"],
    )
    user_agent: str = Field(
        ...,
        title="User Agent",
        description="The user-agent string from the client's request header,"
        " representing the client's browser or other client"
        " application.",
        examples=[
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        ],
    )
    request_path: str = Field(
        ...,
        title="Request path",
        description="The path or endpoint the client is trying to access on"
        " the server.",
        examples=["/api/v1/data"],
    )
