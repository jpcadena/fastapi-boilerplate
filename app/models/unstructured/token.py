"""
A module for token in the app-models package for the Redis database.
"""
from pydantic import BaseModel, ConfigDict, Field

from app.config.config import auth_setting


class Token(BaseModel):
    """
    Token class based on Pydantic Base Model.
    """

    key: str = Field(
        ..., title="Token", description="Refresh token retrieved from login"
    )
    user_info: str = Field(
        ...,
        title="User Info",
        description="User ID and IP address of user",
        pattern=auth_setting.TOKEN_USER_INFO_REGEX,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
                "user_info": "c3ee0ef6-3a18-4251-af6d-138a8c8fec25:127.0.0.1",
            }
        }
    )
