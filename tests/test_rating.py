import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers

rating_data = {
    "rating": 5,
    "review": "Отличная книга!",
    "book_id": 1
}

update_rating_data = {
    "rating": 4,
    "review": "Хорошая книга, но есть недостатки"
}

invalid_rating_data = {
    "rating": 6,
    "review": "A" * 1001,
    "book_id": 9999
}


@pytest.mark.asyncio
async def test_create_rating(test_client: AsyncClient, admin_token: str):
    author = await test_client.post("/authors/", json={"name": "Джоан Роулинг"}, headers=auth_headers(admin_token))
    genre = await test_client.post("/genres/", json={"name": "Фэнтези"}, headers=auth_headers(admin_token))
    book = await test_client.post("/books/", json={
        "title": "Гарри Поттер",
        "publication_year": 1997,
        "author_id": author.json()["id"],
        "genre_ids": [genre.json()["id"]]
    }, headers=auth_headers(admin_token))
    await test_client.post("/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123"
    })
    login = await test_client.post("/login", data={
        "username": "test@example.com",
        "password": "password123"
    })
    token = login.json()["access_token"]

    data = rating_data.copy()
    data["book_id"] = book.json()["id"]
    response = await test_client.post(
        "/ratings/",
        json=data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    result = response.json()
    assert result["rating"] == data["rating"]
    assert result["review"] == data["review"]
    assert result["book_id"] == data["book_id"]
    assert "id" in result

    response = await test_client.post(
        "/ratings/",
        json=data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "already rated" in response.json()["detail"]

    invalid_data = data.copy()
    invalid_data["book_id"] = 9999
    response = await test_client.post(
        "/ratings/",
        json=invalid_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    assert "Book not found" in response.json()["detail"]

    response = await test_client.post(
        "/ratings/",
        json=invalid_rating_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_rating(test_client: AsyncClient, admin_token: str):
    author = await test_client.post("/authors/", json={"name": "Джоан Роулинг"}, headers=auth_headers(admin_token))
    genre = await test_client.post("/genres/", json={"name": "Фэнтези"}, headers=auth_headers(admin_token))
    book = await test_client.post("/books/", json={
        "title": "Гарри Поттер",
        "publication_year": 1997,
        "author_id": author.json()["id"],
        "genre_ids": [genre.json()["id"]]
    }, headers=auth_headers(admin_token))
    await test_client.post("/register", json={
        "email": "test2@example.com",
        "username": "testuser2",
        "password": "password123"
    })
    login = await test_client.post("/login", data={
        "username": "test2@example.com",
        "password": "password123"
    })
    token = login.json()["access_token"]

    data = rating_data.copy()
    data["book_id"] = book.json()["id"]
    create_resp = await test_client.post(
        "/ratings/",
        json=data,
        headers={"Authorization": f"Bearer {token}"}
    )
    rating_id = create_resp.json()["id"]

    response = await test_client.get(
        f"/ratings/{rating_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == rating_id
    assert result["rating"] == data["rating"]
    assert result["review"] == data["review"]

    response = await test_client.get(
        "/ratings/9999",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404

    await test_client.post("/register", json={
        "email": "another@example.com",
        "username": "anotheruser",
        "password": "password123"
    })
    another_login = await test_client.post("/login", data={
        "username": "another@example.com",
        "password": "password123"
    })
    another_token = another_login.json()["access_token"]

    response = await test_client.get(
        f"/ratings/{rating_id}",
        headers={"Authorization": f"Bearer {another_token}"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_user_ratings(test_client: AsyncClient, admin_token: str):
    author = await test_client.post("/authors/", json={"name": "Джоан Роулинг"}, headers=auth_headers(admin_token))
    genre = await test_client.post("/genres/", json={"name": "Фэнтези"}, headers=auth_headers(admin_token))
    book1 = await test_client.post("/books/", json={
        "title": "Гарри Поттер 1",
        "publication_year": 1997,
        "author_id": author.json()["id"],
        "genre_ids": [genre.json()["id"]]
    }, headers=auth_headers(admin_token))
    book2 = await test_client.post("/books/", json={
        "title": "Гарри Поттер 2",
        "publication_year": 1998,
        "author_id": author.json()["id"],
        "genre_ids": [genre.json()["id"]]
    }, headers=auth_headers(admin_token))
    await test_client.post("/register", json={
        "email": "test3@example.com",
        "username": "testuser3",
        "password": "password123"
    })
    login = await test_client.post("/login", data={
        "username": "test3@example.com",
        "password": "password123"
    })
    token = login.json()["access_token"]

    ratings = [
        {"book_id": book1.json()["id"], "rating": 5, "review": "Отлично"},
        {"book_id": book2.json()["id"], "rating": 4, "review": "Хорошо"},
    ]
    for rating in ratings:
        await test_client.post(
            "/ratings/",
            json=rating,
            headers={"Authorization": f"Bearer {token}"}
        )

    response = await test_client.get(
        "/ratings/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert all(isinstance(r, dict) for r in response.json())

    response = await test_client.get(
        "/ratings/?skip=1&limit=1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_update_rating(test_client: AsyncClient, admin_token: str):
    author = await test_client.post("/authors/", json={"name": "Джоан Роулинг"}, headers=auth_headers(admin_token))
    genre = await test_client.post("/genres/", json={"name": "Фэнтези"}, headers=auth_headers(admin_token))
    book = await test_client.post("/books/", json={
        "title": "Гарри Поттер",
        "publication_year": 1997,
        "author_id": author.json()["id"],
        "genre_ids": [genre.json()["id"]]
    }, headers=auth_headers(admin_token))
    await test_client.post("/register", json={
        "email": "test4@example.com",
        "username": "testuser4",
        "password": "password123"
    })
    login = await test_client.post("/login", data={
        "username": "test4@example.com",
        "password": "password123"
    })
    token = login.json()["access_token"]

    data = rating_data.copy()
    data["book_id"] = book.json()["id"]
    create_resp = await test_client.post(
        "/ratings/",
        json=data,
        headers={"Authorization": f"Bearer {token}"}
    )
    rating_id = create_resp.json()["id"]

    response = await test_client.put(
        f"/ratings/{rating_id}",
        json=update_rating_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    result = response.json()
    assert result["rating"] == update_rating_data["rating"]
    assert result["review"] == update_rating_data["review"]

    response = await test_client.put(
        f"/ratings/{rating_id}",
        json={"rating": 3},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["rating"] == 3
    assert response.json()["review"] == update_rating_data["review"]
    response = await test_client.put(
        f"/ratings/{rating_id}",
        json={"rating": 11}, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422

    await test_client.post("/register", json={
        "email": "another2@example.com",
        "username": "anotheruser2",
        "password": "password123"
    })
    another_login = await test_client.post("/login", data={
        "username": "another2@example.com",
        "password": "password123"
    })
    another_token = another_login.json()["access_token"]

    response = await test_client.put(
        f"/ratings/{rating_id}",
        json=update_rating_data,
        headers={"Authorization": f"Bearer {another_token}"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_rating(test_client: AsyncClient, admin_token: str):
    author = await test_client.post("/authors/", json={"name": "Джоан Роулинг"}, headers=auth_headers(admin_token))
    genre = await test_client.post("/genres/", json={"name": "Фэнтези"}, headers=auth_headers(admin_token))
    book = await test_client.post("/books/", json={
        "title": "Гарри Поттер",
        "publication_year": 1997,
        "author_id": author.json()["id"],
        "genre_ids": [genre.json()["id"]]
    }, headers=auth_headers(admin_token))
    await test_client.post("/register", json={
        "email": "test5@example.com",
        "username": "testuser5",
        "password": "password123"
    })
    login = await test_client.post("/login", data={
        "username": "test5@example.com",
        "password": "password123"
    })
    token = login.json()["access_token"]

    data = rating_data.copy()
    data["book_id"] = book.json()["id"]
    create_resp = await test_client.post(
        "/ratings/",
        json=data,
        headers={"Authorization": f"Bearer {token}"}
    )
    rating_id = create_resp.json()["id"]

    response = await test_client.delete(
        f"/ratings/{rating_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204

    response = await test_client.get(
        f"/ratings/{rating_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404

    response = await test_client.delete(
        "/ratings/9999",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404

    await test_client.post("/register", json={
        "email": "another3@example.com",
        "username": "anotheruser3",
        "password": "password123"
    })
    another_login = await test_client.post("/login", data={
        "username": "another3@example.com",
        "password": "password123"
    })
    another_token = another_login.json()["access_token"]

    create_resp = await test_client.post(
        "/ratings/",
        json=data,
        headers={"Authorization": f"Bearer {token}"}
    )
    rating_id = create_resp.json()["id"]

    response = await test_client.delete(
        f"/ratings/{rating_id}",
        headers={"Authorization": f"Bearer {another_token}"}
    )
    assert response.status_code == 403
