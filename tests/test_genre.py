import pytest
from httpx import AsyncClient

genre_data = {
    "name": "Фэнтези"
}

invalid_genre_data = {
    "name": "F"
}

update_genre_data = {
    "name": "Научная фантастика"
}


@pytest.mark.asyncio
async def test_create_genre(test_client: AsyncClient):
    response = await test_client.post("/genres/", json=genre_data)
    assert response.status_code == 201
    assert response.json()["name"] == genre_data["name"]
    assert "id" in response.json()

    response = await test_client.post("/genres/", json=genre_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

    response = await test_client.post("/genres/", json={"name": genre_data["name"].lower()})
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

    response = await test_client.post("/genres/", json=invalid_genre_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_genre(test_client: AsyncClient):
    create_response = await test_client.post("/genres/", json=genre_data)
    genre_id = create_response.json()["id"]

    response = await test_client.get(f"/genres/{genre_id}")
    assert response.status_code == 200
    assert response.json()["id"] == genre_id
    assert response.json()["name"] == genre_data["name"]

    response = await test_client.get("/genres/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_genres_list(test_client: AsyncClient):
    response = await test_client.get("/genres/")
    initial_count = len(response.json())

    test_genres = ["Фэнтези", "Научная фантастика", "Детектив"]
    for name in test_genres:
        await test_client.post("/genres/", json={"name": name})

    response = await test_client.get("/genres/")
    assert response.status_code == 200
    assert len(response.json()) == initial_count + len(test_genres)

    response = await test_client.get("/genres/?skip=1&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_update_genre(test_client: AsyncClient):
    create_response = await test_client.post("/genres/", json=genre_data)
    genre_id = create_response.json()["id"]

    response = await test_client.put(f"/genres/{genre_id}", json=update_genre_data)
    assert response.status_code == 200
    assert response.json()["name"] == update_genre_data["name"]

    await test_client.post("/genres/", json={"name": "Дубликат"})
    response = await test_client.put(f"/genres/{genre_id}", json={"name": "Дубликат"})
    assert response.status_code == 400

    response = await test_client.put(f"/genres/{genre_id}", json=invalid_genre_data)
    assert response.status_code == 422

    response = await test_client.put(f"/genres/{genre_id}", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_genre(test_client: AsyncClient):
    create_response = await test_client.post("/genres/", json=genre_data)
    genre_id = create_response.json()["id"]

    response = await test_client.delete(f"/genres/{genre_id}")
    assert response.status_code == 204

    response = await test_client.get(f"/genres/{genre_id}")
    assert response.status_code == 404

    response = await test_client.delete("/genres/9999")
    assert response.status_code == 404
