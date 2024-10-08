"""
The main script that initiates and runs the FastAPI application.
This module sets up the application configuration including logging,
 CORS, database connection, static files routing and API routes.
"""

import logging
from functools import partial
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import PositiveInt
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_v1.api import api_router
from app.config.config import auth_setting, init_setting, setting
from app.core import logging_config
from app.core.lifecycle import lifespan
from app.db.session import check_db_health, get_db_session
from app.middlewares.blacklist_token import blacklist_middleware

# from app.middlewares.ip_blacklist import IPBlacklistMiddleware
# from app.middlewares.rate_limiter import RateLimiterMiddleware
from app.middlewares.security_headers import SecurityHeadersMiddleware
from app.schemas.schemas import health_example
from app.utils.files_utils.openapi_utils import (
    custom_generate_unique_id,
    custom_openapi,
)

logging_config.setup_logging(setting, init_setting)
logger: logging.Logger = logging.getLogger(__name__)

app: FastAPI = FastAPI(
    debug=True,
    openapi_url=f"{auth_setting.API_V1_STR}{init_setting.OPENAPI_FILE_PATH}",
    openapi_tags=init_setting.TAGS_METADATA,
    lifespan=lifespan,
    generate_unique_id_function=custom_generate_unique_id,
)
app.openapi = partial(custom_openapi, app)  # type: ignore
app.add_middleware(SecurityHeadersMiddleware)
# app.add_middleware(RateLimiterMiddleware)  # type: ignore
# app.add_middleware(IPBlacklistMiddleware)  # type: ignore
app.add_middleware(
    CORSMiddleware,
    allow_origins=setting.BACKEND_CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
app.add_middleware(GZipMiddleware)
app.middleware("http")(blacklist_middleware)
app.mount(
    init_setting.IMAGES_PATH,
    StaticFiles(directory=init_setting.IMAGES_DIRECTORY),
    name=init_setting.IMAGES_APP,
)
app.include_router(api_router, prefix=auth_setting.API_V1_STR)


@app.get(
    "/",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    response_class=RedirectResponse,
)
async def redirect_to_docs() -> RedirectResponse:
    """
    Redirects the user to the /docs endpoint for API documentation.
    ## Response:
    - `return:` **The redirected response**
    - `rtype:` **RedirectResponse**
    """
    return RedirectResponse("/docs")


@app.get(
    "/health",
    responses=health_example,
)
async def check_health(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ORJSONResponse:
    """
    Check the health of the application backend.

    ## Response:
    - `return:` **The ORJSON response**
    - `rtype:` **ORJSONResponse**
    \f
    """
    health_status: dict[str, str] = {
        "status": "healthy",
    }
    status_code: PositiveInt = status.HTTP_200_OK
    if not await check_db_health(session):
        health_status["status"] = "unhealthy"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ORJSONResponse(health_status, status_code=status_code)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=f"{setting.SERVER_HOST}",
        port=setting.SERVER_PORT,
        reload=setting.SERVER_RELOAD,
        log_level=setting.SERVER_LOG_LEVEL,
    )
