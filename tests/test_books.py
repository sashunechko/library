import pytest


@pytest.mark.asyncio
async def test_create_book(client):
    author = await client.post("/api/v1/authors/", json={"first_name": "A", "last_name": "B"})
    author_id = author.json()["id"]
    response = await client.post("/api/v1/books/", json={
        "title": "War and Peace",
        "year": 1869,
        "author_ids": [author_id],
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "War and Peace"
    assert len(data["authors"]) == 1


@pytest.mark.asyncio
async def test_list_books(client):
    response = await client.get("/api/v1/books/")
    assert response.status_code == 200
    assert "items" in response.json()


@pytest.mark.asyncio
async def test_list_books_filter_by_author(client):
    author = await client.post("/api/v1/authors/", json={"first_name": "X", "last_name": "Y"})
    author_id = author.json()["id"]
    await client.post("/api/v1/books/", json={"title": "Book1", "author_ids": [author_id]})
    await client.post("/api/v1/books/", json={"title": "Book2"})
    response = await client.get(f"/api/v1/books/?author_id={author_id}")
    assert response.status_code == 200
    data = response.json()
    assert all(any(a["id"] == author_id for a in b["authors"]) for b in data["items"])


@pytest.mark.asyncio
async def test_get_book(client):
    create = await client.post("/api/v1/books/", json={"title": "Test Book"})
    book_id = create.json()["id"]
    response = await client.get(f"/api/v1/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Book"


@pytest.mark.asyncio
async def test_update_book(client):
    create = await client.post("/api/v1/books/", json={"title": "Old Title"})
    book_id = create.json()["id"]
    response = await client.put(f"/api/v1/books/{book_id}", json={"title": "New Title"})
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"


@pytest.mark.asyncio
async def test_delete_book(client):
    create = await client.post("/api/v1/books/", json={"title": "Delete Me"})
    book_id = create.json()["id"]
    response = await client.delete(f"/api/v1/books/{book_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_create_book_with_isbn(client):
    response = await client.post("/api/v1/books/", json={"title": "ISBN Book", "isbn": "9781234567890"})
    assert response.status_code == 201
    assert response.json()["isbn"] == "9781234567890"
