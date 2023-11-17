"""
Services initialization package
"""
from typing import Optional, TypeVar

from app.models.sql.user import User
from app.schemas.external.user import (
    UserCreateResponse,
    UserResponse,
    UserUpdateResponse,
)

T = TypeVar("T", UserResponse, UserCreateResponse, UserUpdateResponse)


async def model_to_response(model: User, response_model: T) -> Optional[T]:
    """
    Converts a model object to a Pydantic response model
    :param model: Object from Pydantic Base Model class
    :type model: User
    :param response_model: Response model
    :type response_model: T
    :return: Model inherited from SQLAlchemy Declarative Base
    :rtype: Optional[T]
    """
    if not model:
        return None
    return response_model.model_validate(model)
