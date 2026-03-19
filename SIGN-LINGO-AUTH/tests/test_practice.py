import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_practice_submit(async_client: AsyncClient):
    # Need auth first
    # Register/Login helper or fix token generator fixture would be better but keeping it simple
    import random
    rand_int = random.randint(1000, 9999)
    username = f"practice_{rand_int}"
    password = "password"
    
    # Register
    await async_client.post("/api/v1/auth/register", json={
        "username": username,
        "email": f"{username}@test.com",
        "password": password
    })
    
    # Login
    login_res = await async_client.post("/api/v1/auth/login", json={
        "username": username,
        "password": password
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Submit practice
    payload = {
        "letter": "A",
        "strokes": [[10, 10], [20, 20]],
        "language": "ISL"
    }
    
    response = await async_client.post("/api/v1/practice/submit", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Practice submitted successfully!"
    assert "score" in data
