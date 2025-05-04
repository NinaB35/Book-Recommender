import numpy as np
import pytest
from httpx import AsyncClient

from app.routers.user import cosine_similarity
from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_recommendations_no_ratings(test_client: AsyncClient, admin_token: str):
    author = await test_client.post("/authors/", json={"name": "Test Author"}, headers=auth_headers(admin_token))
    genre = await test_client.post("/genres/", json={"name": "Test Genre"}, headers=auth_headers(admin_token))

    books = [
        await test_client.post("/books/", json={
            "title": f"Book {i}",
            "author_id": author.json()["id"],
            "genre_ids": [genre.json()["id"]],
            "publication_year": 2000 + i
        }, headers=auth_headers(admin_token)) for i in range(5)
    ]

    await test_client.post("/register", json={
        "email": "user@test.com",
        "username": "testuser",
        "password": "password"
    })
    login = await test_client.post("/login", data={
        "username": "user@test.com",
        "password": "password"
    })
    token = login.json()["access_token"]

    response = await test_client.get(
        "/recommendations",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 5

    for i in range(5):
        assert response.json()[i]["id"] == books[4 - i].json()["id"]


@pytest.mark.asyncio
async def test_recommendations_with_similar_users(test_client: AsyncClient, admin_token: str):
    author = await test_client.post("/authors/", json={"name": "Test Author"}, headers=auth_headers(admin_token))
    genre = await test_client.post("/genres/", json={"name": "Test Genre"}, headers=auth_headers(admin_token))

    books = [
        await test_client.post("/books/", json={
            "title": f"Book {i}",
            "author_id": author.json()["id"],
            "genre_ids": [genre.json()["id"]],
            "publication_year": 2000 + i
        }, headers=auth_headers(admin_token)) for i in range(10)
    ]
    book_ids = [b.json()["id"] for b in books]

    users = []
    for i in range(3):
        await test_client.post("/register", json={
            "email": f"user{i}@test.com",
            "username": f"user{i}",
            "password": "password"
        })
        login = await test_client.post("/login", data={
            "username": f"user{i}@test.com",
            "password": "password"
        })
        users.append(login.json()["access_token"])

    for book_id in book_ids[:8]:
        await test_client.post("/ratings/",
                               json={"book_id": book_id, "rating": 5},
                               headers={"Authorization": f"Bearer {users[0]}"}
                               )

    for book_id in book_ids[5:]:
        await test_client.post("/ratings/",
                               json={"book_id": book_id, "rating": 5},
                               headers={"Authorization": f"Bearer {users[1]}"}
                               )

    for book_id in book_ids[:5]:
        await test_client.post("/ratings/",
                               json={"book_id": book_id, "rating": 3},
                               headers={"Authorization": f"Bearer {users[2]}"}
                               )

    response = await test_client.get(
        "/recommendations",
        headers={"Authorization": f"Bearer {users[2]}"}
    )

    assert response.status_code == 200
    recommended_books = response.json()
    assert len(recommended_books) > 0

    recommended_ids = [b["id"] for b in recommended_books]
    assert all(bid in book_ids[5:8] for bid in recommended_ids)


@pytest.mark.asyncio
async def test_recommendations_with_low_ratings(test_client: AsyncClient, admin_token: str):
    author = await test_client.post("/authors/", json={"name": "Test Author"}, headers=auth_headers(admin_token))
    genre = await test_client.post("/genres/", json={"name": "Test Genre"}, headers=auth_headers(admin_token))

    books = [
        await test_client.post("/books/", json={
            "title": f"Book {i}",
            "author_id": author.json()["id"],
            "genre_ids": [genre.json()["id"]],
            "publication_year": 2000 + i
        }, headers=auth_headers(admin_token)) for i in range(10)
    ]
    book_ids = [b.json()["id"] for b in books]

    await test_client.post("/register", json={
        "email": "user1@test.com",
        "username": "user1",
        "password": "password"
    })
    login1 = await test_client.post("/login", data={
        "username": "user1@test.com",
        "password": "password"
    })
    token1 = login1.json()["access_token"]

    await test_client.post("/register", json={
        "email": "user2@test.com",
        "username": "user2",
        "password": "password"
    })
    login2 = await test_client.post("/login", data={
        "username": "user2@test.com",
        "password": "password"
    })
    token2 = login2.json()["access_token"]

    for book_id in book_ids:
        await test_client.post("/ratings/",
                               json={"book_id": book_id, "rating": 1},
                               headers={"Authorization": f"Bearer {token1}"}
                               )

    await test_client.post("/ratings/",
                           json={"book_id": book_ids[0], "rating": 3},
                           headers={"Authorization": f"Bearer {token2}"}
                           )

    response = await test_client.get(
        "/recommendations",
        headers={"Authorization": f"Bearer {token2}"}
    )

    assert response.status_code == 200
    recommended_books = response.json()
    assert book_ids[0] not in [b["id"] for b in recommended_books]


@pytest.mark.asyncio
async def test_recommendations_pagination(test_client: AsyncClient, admin_token: str):
    author = await test_client.post("/authors/", json={"name": "Test Author"}, headers=auth_headers(admin_token))
    genre = await test_client.post("/genres/", json={"name": "Test Genre"}, headers=auth_headers(admin_token))

    for i in range(30):
        await test_client.post("/books/", json={
            "title": f"Book {i}",
            "author_id": author.json()["id"],
            "genre_ids": [genre.json()["id"]],
            "publication_year": 2000 + i
        }, headers=auth_headers(admin_token))

    await test_client.post("/register", json={
        "email": "user@test.com",
        "username": "testuser",
        "password": "password"
    })
    login = await test_client.post("/login", data={
        "username": "user@test.com",
        "password": "password"
    })
    token = login.json()["access_token"]

    response = await test_client.get(
        "/recommendations?limit=5",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 5

    first_page = await test_client.get(
        "/recommendations?limit=10&skip=0",
        headers={"Authorization": f"Bearer {token}"}
    )
    second_page = await test_client.get(
        "/recommendations?limit=10&skip=10",
        headers={"Authorization": f"Bearer {token}"}
    )

    first_ids = [b["id"] for b in first_page.json()]
    second_ids = [b["id"] for b in second_page.json()]

    assert len(set(first_ids) & set(second_ids)) == 0


@pytest.mark.asyncio
async def test_cosine_similarity():
    a = np.array([1, 2, 3])
    assert cosine_similarity(a, a) == pytest.approx(1.0)

    b = np.array([-2, 1, 0])
    assert cosine_similarity(a, b) == pytest.approx(0.0)

    c = np.array([-1, -2, -3])
    assert cosine_similarity(a, c) == pytest.approx(-1.0)

    d = np.array([1, 1, 1])
    assert 0 < cosine_similarity(a, d) < 1
