import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers

author_data = {
    "name": "Джоан Роулинг",
    "bio": "Британская писательница, автор серии о Гарри Поттере"
}

invalid_author_data = {
    "name": "A",
    "bio": "Короткая биография"
}

update_author_data = {
    "name": "J.K. Rowling",
    "bio": "British author, best known for Harry Potter"
}


@pytest.mark.asyncio
async def test_create_author_unauthorized(test_client: AsyncClient):
    response = await test_client.post("/authors/", json=author_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_author(test_client: AsyncClient, admin_token: str):
    response = await test_client.post("/authors/", json=author_data, headers=auth_headers(admin_token))
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == author_data["name"]
    assert data["bio"] == author_data["bio"]
    assert "id" in data
    assert data["books_count"] == 0

    response = await test_client.post("/authors/", json=author_data, headers=auth_headers(admin_token))
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

    response = await test_client.post("/authors/", json={"name": author_data["name"].lower()},
                                      headers=auth_headers(admin_token))
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

    response = await test_client.post("/authors/", json=invalid_author_data, headers=auth_headers(admin_token))
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_author(test_client: AsyncClient, admin_token: str):
    create_resp = await test_client.post("/authors/", json=author_data, headers=auth_headers(admin_token))
    author_id = create_resp.json()["id"]

    response = await test_client.get(f"/authors/{author_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == author_id
    assert data["name"] == author_data["name"]
    assert data["bio"] == author_data["bio"]
    assert "books_count" in response.json()

    response = await test_client.get("/authors/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_authors_list(test_client: AsyncClient, admin_token: str):
    response = await test_client.get("/authors/")
    initial_count = len(response.json())

    authors = [
        {"name": "Айзек Азимов", "bio": "Фантаст"},
        {"name": "Стивен Кинг", "bio": "Король ужасов"},
        {"name": "Лев Толстой", "bio": "Русский классик"}
    ]
    for author in authors:
        await test_client.post("/authors/", json=author, headers=auth_headers(admin_token))

    response = await test_client.get("/authors/")
    assert response.status_code == 200
    assert len(response.json()) == initial_count + len(authors)

    response = await test_client.get("/authors/?skip=1&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_update_author(test_client: AsyncClient, admin_token: str):
    create_resp = await test_client.post("/authors/", json=author_data, headers=auth_headers(admin_token))
    author_id = create_resp.json()["id"]

    response = await test_client.put(f"/authors/{author_id}", json=update_author_data,
                                     headers=auth_headers(admin_token))
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_author_data["name"]
    assert data["bio"] == update_author_data["bio"]

    response = await test_client.put(f"/authors/{author_id}", json={"bio": "Новая биография"},
                                     headers=auth_headers(admin_token))
    assert response.status_code == 200
    assert response.json()["name"] == update_author_data["name"]
    assert response.json()["bio"] == "Новая биография"

    await test_client.post("/authors/", json={"name": "Дубликат"}, headers=auth_headers(admin_token))
    response = await test_client.put(f"/authors/{author_id}", json={"name": "Дубликат"},
                                     headers=auth_headers(admin_token))
    assert response.status_code == 400

    response = await test_client.put(f"/authors/{author_id}", json={"name": "A"}, headers=auth_headers(admin_token))
    assert response.status_code == 422

    response = await test_client.put(f"/authors/{author_id}", json={}, headers=auth_headers(admin_token))
    assert response.status_code == 400
    assert response.json()["detail"] == "No data to update"


@pytest.mark.asyncio
async def test_delete_author(test_client: AsyncClient, admin_token: str):
    create_resp = await test_client.post("/authors/", json=author_data, headers=auth_headers(admin_token))
    author_id = create_resp.json()["id"]

    response = await test_client.delete(f"/authors/{author_id}", headers=auth_headers(admin_token))
    assert response.status_code == 204

    response = await test_client.get(f"/authors/{author_id}")
    assert response.status_code == 404

    response = await test_client.delete("/authors/9999", headers=auth_headers(admin_token))
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_author_empty_bio(test_client: AsyncClient, admin_token: str):
    data = {"name": "Новый автор", "bio": ""}
    response = await test_client.post("/authors/", json=data, headers=auth_headers(admin_token))
    assert response.status_code == 201
    assert response.json()["bio"] == ""
