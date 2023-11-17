"""
The main script that initiates and runs the FastAPI application.
This module sets up the application configuration including logging,
 CORS, database connection, static files routing and API routes.
"""
import logging
from functools import partial

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.api_v1.api import api_router
from app.config.config import auth_setting, init_setting, setting
from app.core import logging_config
from app.core.lifecycle import lifespan
from app.middlewares.blacklist_token import blacklist_middleware
from app.middlewares.ip_blacklist import BlacklistMiddleware
from app.middlewares.rate_limiter import RateLimiterMiddleware
from app.middlewares.security_headers import SecurityHeadersMiddleware
from app.utils.files_utils.openapi_utils import (
    custom_generate_unique_id,
    custom_openapi,
)

logging_config.setup_logging(init_settings=init_setting, settings=setting)
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
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(BlacklistMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=setting.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
    return RedirectResponse(url="/docs")
