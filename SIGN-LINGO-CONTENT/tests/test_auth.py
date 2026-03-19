import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    response = await async_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "FastAPI backend is running!"}

@pytest.mark.asyncio
async def test_register_new_user(async_client: AsyncClient):
    payload = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword123",
        "role": "user"
    }
    # Clean up before test if possible, or use random email
    import random
    rand_int = random.randint(1000, 9999)
    payload["username"] = f"testuser_{rand_int}"
    payload["email"] = f"testuser_{rand_int}@example.com"
    
    response = await async_client.post("/api/v1/auth/register", json=payload)
    # Check if DB is reachable, if not 500 might occur
    # Assuming local mongo is running
    assert response.status_code in [201, 400] # 400 if exists
    if response.status_code == 201:
        data = response.json()
        assert data["username"] == payload["username"]
        assert "id" in data

@pytest.mark.asyncio
async def test_login(async_client: AsyncClient):
    # Register first
    import random
    rand_int = random.randint(1000, 9999)
    username = f"loginuser_{rand_int}"
    password = "loginpassword"
    
    await async_client.post("/api/v1/auth/register", json={
        "username": username, 
        "email": f"{username}@example.com", 
        "password": password
    })
    
    response = await async_client.post("/api/v1/auth/login", json={
        "username": username,
        "password": password
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
