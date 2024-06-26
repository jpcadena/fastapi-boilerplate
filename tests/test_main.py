"""
A module for testing the main application in the tests package.
"""

from typing import Any, AsyncGenerator

import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.base_class import Base
from app.db.session import async_engine
from main import app


@pytest.fixture(scope="function")
async def database_fixture() -> AsyncGenerator[AsyncSession, Any]:
    """
    Creates a new database session for a test, creating all tables before the
     test and dropping them after the test completes. Ensures each test runs
     against a clean database.
    """
    async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
        async_engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as session:
        yield session
        await session.rollback()
        await session.close()
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def app_with_lifespan() -> AsyncGenerator[FastAPI, None]:
    """
    A pytest fixture to manage lifespan events for the FastAPI application.
    :return: The FastAPI application with lifespan events managed.
    :rtype: AsyncGenerator[FastAPI, None]
    """
    async with LifespanManager(app) as manager:
        yield manager.app  # type: ignore


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, Any]:
    """
    A pytest fixture to provide an HTTPX AsyncClient configured to communicate
    with the FastAPI application.
    :return: An instance of HTTPX AsyncClient.
    :rtype: AsyncGenerator[AsyncClient, Any]
    """
    async with AsyncClient(app=app, base_url="http://localhost") as client:
        yield client


@pytest.mark.anyio
async def test_redirect_to_docs(client: AsyncClient) -> None:
    """
    Tests whether the root path ``/`` redirects to the documentation page
     ``/docs``.
    :param client: The test client used to make requests to the application.
    :type client: AsyncClient
    :return: None
    :rtype: NoneType
    """
    response: Response = await client.get("/")
    assert response.status_code == 307
    assert response.headers["location"] == "/docs"


@pytest.mark.anyio
async def test_check_health(client: AsyncClient) -> None:
    """
    Tests the health check endpoint ``/health`` of the application.
    :param client: The test client used to make requests to the application.
    :type client: AsyncClient
    :return: None
    :rtype: NoneType
    """
    response: Response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
