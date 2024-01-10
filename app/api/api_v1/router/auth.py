"""
Authentication API Router.
This module provides login and password recovery functionality.
"""
import logging
from typing import Annotated, Any, Optional

from fastapi import (
    APIRouter,
    Body,
    Depends,
    Header,
    HTTPException,
    Path,
    Request,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from redis.asyncio import Redis
from starlette.datastructures import Address

from app.api.deps import get_redis_dep
from app.api.oauth2_validation import get_current_user, get_refresh_current_user
from app.config.config import (
    get_auth_settings,
    get_init_settings,
    get_settings,
    init_setting,
)
from app.config.db.auth_settings import AuthSettings
from app.config.init_settings import InitSettings
from app.config.settings import Settings
from app.core.security.password import verify_password
from app.exceptions.exceptions import NotFoundException, ServiceException
from app.models.sql.user import User as UserDB
from app.schemas.external.msg import Msg
from app.schemas.external.token import TokenResetPassword, TokenResponse
from app.schemas.external.user import (
    UserResponse,
    UserUpdate,
    UserUpdateResponse,
)
from app.schemas.infrastructure.user import UserAuth
from app.services.infrastructure.auth import common_auth_procedure
from app.services.infrastructure.token import TokenService
from app.services.infrastructure.user import UserService, get_user_service
from app.tasks.email_tasks.email_tasks import (
    send_password_changed_confirmation_email,
    send_reset_password_email,
)
from app.utils.security.password import (
    generate_password_reset_token,
    verify_password_reset_token,
)

logger: logging.Logger = logging.getLogger(__name__)
router: APIRouter = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    auth_settings: Annotated[AuthSettings, Depends(get_auth_settings)],
    user: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: Annotated[UserService, Depends(get_user_service)],
    redis: Annotated[Redis, Depends(get_redis_dep)],  # type: ignore
) -> TokenResponse:
    """
    Endpoint to handle user login with OAuth2 authentication using
     request form.
    ## Parameter:
    - `user:` **Request body with username and password**
    - `type:` **OAuth2PasswordRequestForm**
    ## Response:
    - `return:` **Token information with access token, its type and
     refresh token**
    - `rtype:` **TokenResponse**
    \f
    :param request: Request object for client host information
    :type request: Request
    :param user_service: Dependency method for User Service
    :type user_service: UserService
    :param auth_settings: Dependency method for cached setting object
    :type auth_settings: AuthSettings
    :param redis: Dependency method for async Redis connection
    :type redis: Redis
    """
    client: Optional[Address] = request.client
    if not client:
        raise NotFoundException(auth_settings.NO_CLIENT_FOUND)
    client_ip: str = client.host
    try:
        found_user: UserDB = await user_service.get_login_user(user.username)
    except ServiceException as exc:
        logger.error(exc)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials"
        ) from exc
    if not verify_password(found_user.password, user.password):
        detail: str = "Incorrect password"
        logger.warning(detail)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=detail
        )
    if not found_user.is_active:
        user_detail: str = "Inactive user"
        logger.warning(user_detail)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=user_detail
        )
    return await common_auth_procedure(
        found_user, client_ip, redis, auth_settings
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def refresh_token(
    request: Request,
    user_service: Annotated[UserService, Depends(get_user_service)],
    auth_settings: Annotated[AuthSettings, Depends(get_auth_settings)],
    refresh_current_user: Annotated[
        UserAuth, Depends(get_refresh_current_user)
    ],
    redis: Annotated[Redis, Depends(get_redis_dep)],  # type: ignore
) -> TokenResponse:
    """
    Generates a refresh token for the current user and saves it to the
     database
     ## Response:
    - `return:` **Token information with access token, its type and
     refresh token**
    - `rtype:` **TokenResponse**
    \f
    :param request: The HTTP request on the server
    :type request: Request
    :param user_service: Dependency method for User Service
    :type user_service: UserService
    :param auth_settings: Dependency method for cached setting object
    :type auth_settings: AuthSettings
    :param refresh_current_user: The current user dependency for refresh token
    :type refresh_current_user: UserAuth
    :param redis: Dependency method for async Redis connection
    :type redis: Redis
    """
    client: Optional[Address]
    if not (client := request.client):
        raise NotFoundException(auth_settings.NO_CLIENT_FOUND)
    client_ip: str = client.host
    try:
        user: UserDB = await user_service.get_login_user(
            refresh_current_user.username
        )
    except ServiceException as exc:
        detail: str = "Can not found user information."
        logger.error(detail)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=detail
        ) from exc
    return await common_auth_procedure(user, client_ip, redis, auth_settings)


@router.post("/validate-token", response_model=UserAuth)
async def validate_token(
    current_user: Annotated[UserAuth, Depends(get_current_user)]
) -> UserAuth:
    """
    Endpoint to validate an access token.
    ## Response:
    - `return:` **The authenticated user instance**
    - `rtype:` **UserAuth**
    \f
    :param current_user: The current user
    :type current_user: UserAuth
    """
    return current_user


@router.post("/recover-password/{email}", response_model=Msg)
async def recover_password(
    settings: Annotated[Settings, Depends(get_settings)],
    auth_settings: Annotated[AuthSettings, Depends(get_auth_settings)],
    email: Annotated[
        EmailStr,
        Path(
            ...,
            title="Email",
            description="The email used to recover the password",
            example={"email": "someone@example.com"},
            openapi_examples=init_setting.EMAIL_BODY_EXAMPLES,
        ),
    ],
    user_service: Annotated[UserService, Depends(get_user_service)],
    init_settings: Annotated[InitSettings, Depends(get_init_settings)],
) -> Msg:
    """
    Endpoint to handle password recovery.
    ## Parameter:
    - `email:` **Path parameter that references the email used to recover
     the password**
    - `type:` **EmailStr**
    ## Response:
    - `return:` **Message object**
    - `rtype:` **Msg**
    \f
    :param user_service: Dependency method for User service object
    :type user_service: UserService
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :param auth_settings: Dependency method for cached setting object
    :type auth_settings: AuthSettings
    :param init_settings: Dependency method for cached init setting object
    :type init_settings: InitSettings
    """
    try:
        user: Optional[UserResponse] = await user_service.get_user_by_email(
            email
        )
    except ServiceException as exc:
        logger.error(exc)
        user = None
    if user:
        password_reset_token: str = generate_password_reset_token(
            email, auth_settings
        )
        await send_reset_password_email(
            user.email,
            user.username,
            password_reset_token,
            settings,
            init_settings,
            auth_settings,
        )
    return Msg(msg="If the email is registered, a reset link will be sent.")


@router.post("/reset-password", response_model=Msg)
async def reset_password(
    settings: Annotated[Settings, Depends(get_settings)],
    auth_settings: Annotated[AuthSettings, Depends(get_auth_settings)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    token_reset_password: Annotated[
        TokenResetPassword,
        Body(
            ...,
            title="Body object",
            description="Object with access token and new password",
            openapi_examples=init_setting.TOKEN_PAYLOAD_EXAMPLES,
        ),
    ],
    init_settings: Annotated[InitSettings, Depends(get_init_settings)],
) -> Msg:
    """
    Endpoint to handle password reset.
    ## Parameter:
    - `token_reset_password:` **Body Object with token and new password**
    - `type:` **TokenResetPassword**
    ## Response:
    - `return:` **Message object**
    - `rtype:` **Msg**
    \f
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :param user_service: Dependency method for User service object
    :type user_service: UserService
    :param auth_settings: Dependency method for cached setting object
    :type auth_settings: AuthSettings
    :param init_settings: Dependency method for cached init setting object
    :type init_settings: InitSettings
    """
    email: Optional[EmailStr] = verify_password_reset_token(
        token_reset_password.token, auth_settings
    )
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )
    try:
        found_user: Optional[
            UserResponse
        ] = await user_service.get_user_by_email(email)
    except ServiceException as exc:
        logger.error(exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There was an issue with the request",
        ) from exc
    if not found_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    user_data: dict[str, Any] = found_user.model_dump()
    user_data["password"] = token_reset_password.password
    user_update: UserUpdate = UserUpdate(**user_data)
    user: UserUpdateResponse = await user_service.update_user(  # type: ignore
        found_user.id, user_update
    )
    await send_password_changed_confirmation_email(
        user.email,
        user.username,
        init_settings,
        settings,
    )
    return Msg(msg=f"Password updated successfully for {user.email}")


@router.post(
    "/logout",
    response_model=Msg,
)
async def logout(
    auth_settings: Annotated[AuthSettings, Depends(get_auth_settings)],
    authorization: Annotated[
        str,
        Header(
            ...,
            title="Authorization",
            description="The access bearer token as authorization string in the"
            " header",
            min_length=30,
            example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
            openapi_examples=init_setting.AUTHORIZATION_HEADER_EXAMPLES,
        ),
    ],
    current_user: Annotated[UserAuth, Depends(get_current_user)],
    redis: Annotated[Redis, Depends(get_redis_dep)],  # type: ignore
) -> Msg:
    """
    Add the user's token to the blacklist database
    ## Parameters:
    - `:param authorization:` **The access bearer token as authorization string
    in the header**
    - `:type authorization:` **str**
     ## Response:
    - `return:` **Message object**
    - `rtype:` **Msg**
    \f
    :param auth_settings: Dependency method for cached setting object
    :type auth_settings: AuthSettings
    :param current_user: The current user
    :type current_user: UserAuth
    :param redis: Dependency method for async Redis connection
    :type redis: Redis
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing.",
        )
    token: str = authorization.replace("Bearer ", "", 1)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing."
        )
    token_service: TokenService = TokenService(redis, auth_settings)
    try:
        blacklisted: bool = await token_service.blacklist_token(token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc
    if not blacklisted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not blacklist the token.",
        )
    return Msg(msg="Logged out successfully")
