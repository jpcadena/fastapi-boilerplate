"""
Services initialization package
"""
from typing import Any, Optional, TypeVar

from sqlalchemy import inspect

from app.db.base_class import Base
from app.schemas.external.address import Address
from app.schemas.external.user import (
    UserCreateResponse,
    UserResponse,
    UserUpdateResponse,
)

T = TypeVar("T", UserResponse, UserCreateResponse, UserUpdateResponse, Address)


async def model_to_response(
    model: Base, response_model: T  # type: ignore
) -> Optional[T]:
    """
    Converts a SQLAlchemy model to a Pydantic Base Model
    :param model: Object from SQLAlchemy base model
    :type model: Base
    :param response_model: Response model to convert
    :type response_model: T
    :return: Model inherited from Pydantic base model
    :rtype: Optional[T]
    """
    return response_model.model_validate(model) if model else None


def model_to_dict(obj: Base) -> dict[str, Any]:  # type: ignore
    """
    Converts a model object (SQLAlchemy Base) to a dictionary
    :param obj: The model object
    :type obj: Base
    :return: The typed dictionary
    :rtype: dict[str, Any]
    """
    return {
        column.key: getattr(obj, column.key)
        for column in inspect(obj).mapper.column_attrs  # type: ignore
    }
