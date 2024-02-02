"""
Centralized API routing script.
This module integrates the individual routers from the different
 modules of the API.
"""

from fastapi import APIRouter

from app.api.api_v1.router import auth, user

api_router: APIRouter = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(user.router)
