import pytest
import httpx
from faker import Faker
import jwt
from datetime import datetime, timedelta

fake = Faker()

KONG_URL = "http://localhost:8000"
GATEWAY_URL = "http://localhost:8000" # FastAPI Gateway also runs on 8000
AUTH_URL = "http://localhost:5002"
CONTENT_URL = "http://localhost:5003"
PRACTICE_URL = "http://localhost:5004"

# The same secret embedded in SIGN-LINGO-KONG/.env and backend environments
JWT_SECRET = "your_secret_key_here_change_this_in_production"

@pytest.fixture(scope="session")
def api_client():
    """Returns a fast HTTPX client for direct routing."""
    with httpx.Client(timeout=15.0) as client:
        yield client

@pytest.fixture(scope="session")
def async_api_client():
    """Returns an async HTTPX client for load testing."""
    return httpx.AsyncClient(timeout=15.0)

@pytest.fixture
def mock_user_payload():
    return {
        "email": fake.email(),
        "password": "Password123!",
        "full_name": fake.name()
    }

@pytest.fixture
def valid_jwt_token():
    """Mints a mathematically perfect JWT token bypassing the DB for gateway testing."""
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode = {
        "exp": expire, 
        "iss": "signlingo-issuer",
        "user_id": "60f7a92b8d0c9a00155b4a1c" # Dummy Mongo ObjectId
    }
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")
    return encoded_jwt

@pytest.fixture
def auth_headers(valid_jwt_token):
    """Returns the Kong-compatible standard Authorization header."""
    return {"Authorization": f"Bearer {valid_jwt_token}"}
