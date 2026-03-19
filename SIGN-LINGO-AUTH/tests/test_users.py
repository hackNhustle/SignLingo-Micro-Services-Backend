import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_update_user_profile(async_client: AsyncClient):
    # 1. Register a user
    import random
    rand_int = random.randint(1000, 9999)
    username = f"update_user_{rand_int}"
    email = f"update_{rand_int}@example.com"
    password = "password123"
    
    reg_res = await async_client.post("/api/v1/auth/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    assert reg_res.status_code == 201
    
    # 2. Login to get token
    login_res = await async_client.post("/api/v1/auth/login", json={
        "username": username,
        "password": password
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Update Profile (change email)
    new_email = f"new_email_{rand_int}@example.com"
    update_res = await async_client.put("/api/v1/user/profile", json={
        "email": new_email
    }, headers=headers)
    
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["email"] == new_email
    assert data["username"] == username # Should remain same
    
    # 4. Verify persistence by fetching profile again
    get_res = await async_client.get("/api/v1/user/profile", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["email"] == new_email

@pytest.mark.asyncio
async def test_update_duplicate_username(async_client: AsyncClient):
    # Create User A
    await async_client.post("/api/v1/auth/register", json={
        "username": "userA",
        "email": "userA@example.com",
        "password": "password"
    })
    
    # Create User B
    await async_client.post("/api/v1/auth/register", json={
        "username": "userB",
        "email": "userB@example.com",
        "password": "password"
    })
    
    # Login as User B
    login_res = await async_client.post("/api/v1/auth/login", json={
        "username": "userB",
        "password": "password"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to update User B's username to "userA" (should fail)
    update_res = await async_client.put("/api/v1/user/profile", json={
        "username": "userA"
    }, headers=headers)
    
    assert update_res.status_code == 409
    assert "Username already taken" in update_res.json()["detail"]
