"""
A module for msg in the app schemas package.
"""
from pydantic import BaseModel, ConfigDict, Field


class Msg(BaseModel):
    """
    Schema for representing a message.
    """

    model_config = ConfigDict(
        json_schema_extra={"example": {"msg": "Hello, World!!!"}}
    )

    msg: str = Field(..., title="Message", description="Message to display")
