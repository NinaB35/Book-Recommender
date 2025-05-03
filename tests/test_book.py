import pytest
from httpx import AsyncClient

book_data = {
    "title": "Гарри Поттер и философский камень",
    "publication_year": 1997,
    "author_id": 1,
    "genre_ids": [1, 2]
}

invalid_book_data = {
    "title": "A",
    "publication_year": 999,
    "author_id": 999,
    "genre_ids": []
}

update_book_data = {
    "title": "Гарри Поттер и Тайная комната",
    "publication_year": 1998,
    "genre_ids": [2, 3]
}

partial_update_data = {
    "title": "Обновленное название"
}


@pytest.mark.asyncio
async def test_create_book(test_client: AsyncClient):
    author = await test_client.post("/authors/", json={"name": "Джоан Роулинг"})
    genre1 = await test_client.post("/genres/", json={"name": "Фэнтези"})
    genre2 = await test_client.post("/genres/", json={"name": "Приключения"})

    data = book_data.copy()
    data["author_id"] = author.json()["id"]
    data["genre_ids"] = [genre1.json()["id"], genre2.json()["id"]]

    response = await test_client.post("/books/", json=data)
    assert response.status_code == 201
    result = response.json()
    assert result["title"] == data["title"]
    assert result["publication_year"] == data["publication_year"]
    assert result["author"]["id"] == data["author_id"]
    assert len(result["genres"]) == 2
    assert result["genres"][0]["id"] in data["genre_ids"]
    assert result["average_rating"] == 0.0

    invalid_data = data.copy()
    invalid_data["author_id"] = 9999
    response = await test_client.post("/books/", json=invalid_data)
    assert response.status_code == 404
    assert "Author not found" in response.json()["detail"]

    invalid_data = data.copy()
    invalid_data["genre_ids"] = [9999]
    response = await test_client.post("/books/", json=invalid_data)
    assert response.status_code == 404
    assert "genres not found" in response.json()["detail"]

    response = await test_client.post("/books/", json=invalid_book_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_book(test_client: AsyncClient):
    author = await test_client.post("/authors/", json={"name": "Джоан Роулинг"})
    genre1 = await test_client.post("/genres/", json={"name": "Фэнтези"})
    genre2 = await test_client.post("/genres/", json={"name": "Приключения"})

    data = book_data.copy()
    data["author_id"] = author.json()["id"]
    data["genre_ids"] = [genre1.json()["id"], genre2.json()["id"]]

    create_resp = await test_client.post("/books/", json=data)
    book_id = create_resp.json()["id"]

    response = await test_client.get(f"/books/{book_id}")
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == book_id
    assert result["title"] == data["title"]
    assert result["author"]["id"] == data["author_id"]
    assert len(result["genres"]) == 2
    assert result["genres"][0]["id"] in data["genre_ids"]

    response = await test_client.get("/books/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_books_list(test_client: AsyncClient):
    author1 = await test_client.post("/authors/", json={"name": "Джоан Роулинг"})
    author2 = await test_client.post("/authors/", json={"name": "Дж. Р. Р. Толкин"})
    genre1 = await test_client.post("/genres/", json={"name": "Фэнтези"})
    genre2 = await test_client.post("/genres/", json={"name": "Приключения"})

    books_data = [
        {
            "title": "Гарри Поттер и философский камень",
            "publication_year": 1997,
            "author_id": author1.json()["id"],
            "genre_ids": [genre1.json()["id"]]
        },
        {
            "title": "Властелин Колец",
            "publication_year": 1954,
            "author_id": author2.json()["id"],
            "genre_ids": [genre1.json()["id"], genre2.json()["id"]]
        }
    ]

    for book in books_data:
        await test_client.post("/books/", json=book)

    response = await test_client.get("/books/")
    assert response.status_code == 200
    assert len(response.json()) >= 2

    response = await test_client.get(f"/books/?author_id={author1.json()['id']}")
    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert all(book["author"]["id"] == author1.json()["id"] for book in response.json())

    response = await test_client.get(f"/books/?genre_id={genre1.json()['id']}")
    assert response.status_code == 200
    assert len(response.json()) >= 2

    response = await test_client.get("/books/?year_from=1990&year_to=2000")
    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert all(1990 <= book["publication_year"] <= 2000 for book in response.json())

    response = await test_client.get("/books/?skip=1&limit=1")
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_update_book(test_client: AsyncClient):
    author1 = await test_client.post("/authors/", json={"name": "Джоан Роулинг"})
    author2 = await test_client.post("/authors/", json={"name": "Дж. Р. Р. Толкин"})
    genre1 = await test_client.post("/genres/", json={"name": "Фэнтези"})
    genre2 = await test_client.post("/genres/", json={"name": "Приключения"})
    genre3 = await test_client.post("/genres/", json={"name": "Детская литература"})

    data = book_data.copy()
    data["author_id"] = author1.json()["id"]
    data["genre_ids"] = [genre1.json()["id"], genre2.json()["id"]]

    create_resp = await test_client.post("/books/", json=data)
    book_id = create_resp.json()["id"]

    update_data = update_book_data.copy()
    update_data["author_id"] = author2.json()["id"]
    update_data["genre_ids"] = [genre2.json()["id"], genre3.json()["id"]]

    response = await test_client.put(f"/books/{book_id}", json=update_data)
    assert response.status_code == 200
    result = response.json()
    assert result["title"] == update_data["title"]
    assert result["publication_year"] == update_data["publication_year"]
    assert result["author"]["id"] == update_data["author_id"]
    assert len(result["genres"]) == 2
    assert all(g["id"] in update_data["genre_ids"] for g in result["genres"])

    response = await test_client.put(f"/books/{book_id}", json=partial_update_data)
    assert response.status_code == 200
    assert response.json()["title"] == partial_update_data["title"]
    assert response.json()["publication_year"] == update_data["publication_year"]

    invalid_data = partial_update_data.copy()
    invalid_data["author_id"] = 9999
    response = await test_client.put(f"/books/{book_id}", json=invalid_data)
    assert response.status_code == 404

    invalid_data = partial_update_data.copy()
    invalid_data["genre_ids"] = [9999]
    response = await test_client.put(f"/books/{book_id}", json=invalid_data)
    assert response.status_code == 404

    response = await test_client.put(f"/books/{book_id}", json={})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_delete_book(test_client: AsyncClient):
    author = await test_client.post("/authors/", json={"name": "Джоан Роулинг"})
    genre = await test_client.post("/genres/", json={"name": "Фэнтези"})

    data = book_data.copy()
    data["author_id"] = author.json()["id"]
    data["genre_ids"] = [genre.json()["id"]]

    create_resp = await test_client.post("/books/", json=data)
    book_id = create_resp.json()["id"]

    response = await test_client.delete(f"/books/{book_id}")
    assert response.status_code == 204

    response = await test_client.get(f"/books/{book_id}")
    assert response.status_code == 404

    response = await test_client.delete("/books/9999")
    assert response.status_code == 404
