import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(test_client: AsyncClient):
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "securepassword123"
    }

    response = await test_client.post("/register", json=user_data)
    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]
    assert response.json()["username"] == user_data["username"]

    response = await test_client.post("/register", json=user_data)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login(test_client: AsyncClient):
    user_data = {
        "email": "login@test.com",
        "username": "loginuser",
        "password": "loginpass"
    }
    await test_client.post("/register", json=user_data)

    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = await test_client.post("/login", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

    response = await test_client.post("/login", data={
        "username": user_data["email"],
        "password": "wrong"
    })
    assert response.status_code == 401
