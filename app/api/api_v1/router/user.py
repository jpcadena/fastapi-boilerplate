"""
User API Router
This module provides CRUD (Create, Retrieve, Update, Delete) operations
 for users.
"""
import logging
from typing import Annotated, Any, Optional
from uuid import uuid4

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    HTTPException,
    Response,
    status,
)
from fastapi.params import Path, Query
from pydantic import UUID4, NonNegativeInt, PositiveInt
from redis.asyncio import Redis
from sqlalchemy.exc import SQLAlchemyError

from app.api.deps import get_redis_dep
from app.api.oauth2_validation import get_current_user
from app.config.config import (
    get_auth_settings,
    get_init_settings,
    get_settings,
    init_setting,
)
from app.config.db.auth_settings import AuthSettings
from app.config.init_settings import InitSettings
from app.config.settings import Settings
from app.exceptions.exceptions import NotFoundException, ServiceException
from app.schemas.external.user import (
    UserAuth,
    UserCreate,
    UserCreateResponse,
    UserResponse,
    UsersResponse,
    UserUpdate,
    UserUpdateResponse,
)
from app.services.infrastructure.cached_user import CachedUserService
from app.services.infrastructure.user import (
    UserService,
    get_user_service,
)
from app.tasks.email_tasks.email_tasks import (
    send_new_account_email,
    send_welcome_email,
)

logger: logging.Logger = logging.getLogger(__name__)
router: APIRouter = APIRouter(prefix="/user", tags=["user"])


@router.get("", response_model=UsersResponse)
async def get_users(
    current_user: Annotated[UserAuth, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    skip: Annotated[
        NonNegativeInt,
        Query(
            annotation=Optional[NonNegativeInt],
            title="Skip",
            description="Skip users",
            example=0,
            openapi_examples=init_setting.SKIP_EXAMPLES,
        ),
    ] = 0,
    limit: Annotated[
        Optional[PositiveInt],
        Query(
            annotation=Optional[PositiveInt],
            title="Limit",
            description="Limit pagination",
            ge=1,
            le=100,
            example=100,
            openapi_examples=init_setting.LIMIT_EXAMPLES,
        ),
    ] = 100,
) -> UsersResponse:
    """
    Retrieve all users' basic information from the system using
     pagination.
    ## Parameters:
    - `:param skip:` **Offset from where to start returning users**
    - `:type skip:` **NonNegativeInt**
    - `:param limit:` **Limit the number of results from query**
    - `:type limit:` **PositiveInt**
    ## Response:
    - `:return:` **List of Users retrieved from database**
    - `:rtype:` **UsersResponse**
    \f
    :param user_service: Dependency method for user service layer
    :type user_service: UserService
    :param current_user: Dependency method for authorization by current user
    :type current_user: UserAuth
    """
    try:
        found_users: list[UserResponse] = await user_service.get_users(
            skip, limit
        )
    except ServiceException as exc:
        logger.error(exc)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    users: UsersResponse = UsersResponse(users=found_users)
    return users


@router.post(
    "", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(
    background_tasks: BackgroundTasks,
    user: Annotated[
        UserCreate,
        Body(
            ...,
            title="User data",
            description="User data to create",
            openapi_examples=init_setting.USER_CREATE_EXAMPLES,
        ),
    ],
    user_service: Annotated[UserService, Depends(get_user_service)],
    auth_settings: Annotated[AuthSettings, Depends(get_auth_settings)],
    init_settings: Annotated[InitSettings, Depends(get_init_settings)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserCreateResponse:
    """
    Register new user into the system.
    ## Parameter:
    - `:param user:` **Body Object for user creation.**
    - `:type user:` **UserCreate**
    ## Response:
    - `:return:` **User created with its data**
    - `:rtype:` **UserCreateResponse**
    \f
    :param background_tasks: Used for sending an email to confirm
     registration in the background
    :type background_tasks: BackgroundTasks
    :param auth_settings: Dependency method for cached setting object
    :type auth_settings: AuthSettings
    :param init_settings: Dependency method for cached init setting object
    :type init_settings: InitSettings
    :param settings: Dependency method for cached setting object
    :type settings: Settings
    :param user_service: Dependency method for user service layer
    :type user_service: UserService
    """
    try:
        new_user: Optional[
            UserCreateResponse
        ] = await user_service.register_user(user)
    except ServiceException as exc:
        detail: str = "Error at creating user."
        logger.error(detail)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail
        ) from exc
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User could not be created",
        )
    if user.email:
        background_tasks.add_task(
            send_new_account_email,
            email_to=user.email,
            username=user.username,
            settings=settings,
            auth_settings=auth_settings,
            init_settings=init_settings,
        )
        background_tasks.add_task(
            send_welcome_email,
            email_to=user.email,
            username=user.username,
            init_settings=init_settings,
            settings=settings,
        )
    return new_user


@router.get("/me", response_model=UserResponse)
async def get_user_me(
    current_user: Annotated[UserAuth, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    redis: Annotated[Redis, Depends(get_redis_dep)],  # type: ignore
) -> UserResponse:
    """
    Retrieve the current user's information.
    ## Response:
    - `:return:` **Response object for current user**
    - `:rtype:` **UserResponse**
    \f
    :param current_user: Dependency method for authorization by current user
    :type current_user: UserAuth
    :param user_service: Dependency method for user service layer
    :type user_service: UserService
    :param redis: Dependency method for async Redis connection
    :type redis: Redis
    """
    cached_service: CachedUserService = CachedUserService(redis)
    cached_user: Optional[
        UserResponse
    ] = await cached_service.get_schema_from_cache(current_user.id)
    if cached_user is not None:
        return cached_user
    try:
        user: UserResponse = await user_service.get_user_by_id(  # type: ignore
            current_user.id
        )
        await cached_service.set_to_cache(current_user.id, user.model_dump())
    except ServiceException as exc:
        detail: str = "Can not found user information."
        logger.error(detail)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=detail
        ) from exc
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[UserAuth, Depends(get_current_user)],
    user_id: Annotated[
        UUID4,
        Path(
            ...,
            title="User ID",
            annotation=UUID4,
            description="ID of the User to be searched",
            examples=[uuid4().__str__()],
        ),
    ],
    redis: Annotated[Redis, Depends(get_redis_dep)],  # type: ignore
) -> UserResponse:
    """
    Retrieve an existing user's information given their user ID.
    ## Parameter:
    - `:param user_id:` **Unique identifier of the user to be retrieved**
    - `:type user_id:` **UUID4**
    ## Response:
    - `:return:` **Found user with the given ID.**
    - `:rtype:` **UserResponse**
    \f
    :param user_service: Dependency method for user service layer
    :type user_service: UserService
    :param current_user: Dependency method for authorization by current user
    :type current_user: UserAuth
    :param redis: Dependency method for async Redis connection
    :type redis: Redis
    """
    cached_service: CachedUserService = CachedUserService(redis)
    cached_user: Optional[
        UserResponse
    ] = await cached_service.get_schema_from_cache(user_id)
    if cached_user is not None:
        return cached_user
    try:
        user: UserResponse = await user_service.get_user_by_id(  # type: ignore
            user_id
        )
        await cached_service.set_to_cache(user_id, user.model_dump())
    except ServiceException as exc:
        detail: str = f"User with id {user_id} not found in the system."
        logger.error(detail)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=detail
        ) from exc
    except NotFoundException as not_found_exc:
        logger.error(not_found_exc)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(not_found_exc)
        ) from not_found_exc
    return user


@router.put("/{user_id}", response_model=UserUpdateResponse)
async def update_user(
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[UserAuth, Depends(get_current_user)],
    user_id: Annotated[
        UUID4,
        Path(
            ...,
            title="User ID",
            annotation=UUID4,
            description="ID of the User to be searched",
            example=uuid4(),
        ),
    ],
    user_in: Annotated[
        UserUpdate,
        Body(
            ...,
            title="User data",
            description="New user data to update",
            openapi_examples=init_setting.USER_UPDATE_EXAMPLES,
        ),
    ],
) -> Optional[UserUpdateResponse]:
    """
    Update an existing user's information given their user ID and new
     information.
    ## Parameters:
    - `:param user_id:` **Unique identifier of the user to be updated**
    - `:type user_id:` **UUID4**
    - `:param user_in:` **New user data to update that can include:
     username, email, first_name, middle_name, last_name, password,
      gender, birthdate, phone_number, city and country.**
    - `:type user_in:` **UserUpdate**
    ## Response:
    - `:return:` **Updated user with the given ID and its data**
    - `:rtype:` **UserUpdateResponse**
    \f
    :param user_service: Dependency method for user service layer
    :type user_service: UserService
    :param current_user: Dependency method for authorization by current user
    :type current_user: UserAuth
    """
    try:
        user: Optional[UserUpdateResponse] = await user_service.update_user(
            user_id, user_in
        )
    except ServiceException as exc:
        detail: str = f"User with id {user_id} not found in the system."
        logger.error(detail)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail
        ) from exc
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[UserAuth, Depends(get_current_user)],
    user_id: Annotated[
        UUID4,
        Path(
            ...,
            title="User ID",
            annotation=UUID4,
            description="ID of the User to be searched",
            example=uuid4(),
        ),
    ],
) -> Response:
    """
    Delete an existing user given their user ID.
    ## Parameter:
    - `:param user_id:` **Unique identifier of the user to be deleted**
    - `:type user_id:` **UUID4**
    ## Response:
    - `:return:` **Json Response object with the deleted information**
    - `:rtype:` **Response**
    \f
    :param user_service: Dependency method for user service layer
    :type user_service: UserService
    :param current_user: Dependency method for authorization by current user
    :type current_user: UserAuth
    """
    try:
        data: dict[str, Any] = await user_service.delete_user(user_id)
    except SQLAlchemyError as sa_err:
        detail: str = "The user with this username does not exist in the system"
        logger.error(detail)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail
        ) from sa_err
    response: Response = Response(
        status_code=status.HTTP_204_NO_CONTENT, media_type="application/json"
    )
    response.headers["deleted"] = str(data["ok"]).lower()
    response.headers["deleted_at"] = str(data["deleted_at"])
    return response
