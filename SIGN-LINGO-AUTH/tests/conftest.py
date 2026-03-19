import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient
try:
    from mongomock_motor import AsyncMongoMockClient
except ImportError:
    # Fallback to real mongo if mock not installed, but tests might fail
    AsyncMongoMockClient = None

from main import app
from core.config import settings
from db.database import mongo

@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
async def async_client() -> AsyncGenerator:
    # Use mock client if available
    if AsyncMongoMockClient:
        mongo.client = AsyncMongoMockClient()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
