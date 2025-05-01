import pytest
from fastapi.testclient import TestClient

author_data = {
    "name": "Джоан Роулинг",
    "bio": "Автор Гарри Поттера"
}


@pytest.mark.asyncio
async def test_create_author(test_client: TestClient):
    response = test_client.post("/authors/", json=author_data)
    assert response.status_code == 201
    assert response.json()["name"] == author_data["name"]
    assert response.json()["bio"] == author_data["bio"]
    assert "id" in response.json()

    response = test_client.post("/authors/", json=author_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_author(test_client: TestClient):
    create_response = test_client.post("/authors/", json=author_data)
    author_id = create_response.json()["id"]

    response = test_client.get(f"/authors/{author_id}")
    assert response.status_code == 200
    assert response.json()["id"] == author_id
    assert response.json()["name"] == author_data["name"]
    assert response.json()["bio"] == author_data["bio"]

    response = test_client.get("/authors/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_author(test_client: TestClient):
    create_response = test_client.post("/authors/", json=author_data)
    author_id = create_response.json()["id"]

    update_data = {"name": "Новое имя"}
    response = test_client.put(f"/authors/{author_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]
    assert response.json()["bio"] == author_data["bio"]

    response = test_client.put(f"/authors/{author_id}", json={"name": "a"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_author(test_client: TestClient):
    create_response = test_client.post("/authors/", json=author_data)
    author_id = create_response.json()["id"]

    response = test_client.delete(f"/authors/{author_id}")
    assert response.status_code == 204

    response = test_client.get(f"/authors/{author_id}")
    assert response.status_code == 404
