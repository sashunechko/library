import pytest


@pytest.mark.asyncio
async def test_create_copy(client):
    book = await client.post("/api/v1/books/", json={"title": "Copy Book"})
    book_id = book.json()["id"]
    response = await client.post(f"/api/v1/books/{book_id}/copies")
    assert response.status_code == 201
    data = response.json()
    assert data["book_id"] == book_id
    assert data["status"] == "available"


@pytest.mark.asyncio
async def test_list_copies(client):
    book = await client.post("/api/v1/books/", json={"title": "List Copies Book"})
    book_id = book.json()["id"]
    await client.post(f"/api/v1/books/{book_id}/copies")
    response = await client.get(f"/api/v1/books/{book_id}/copies")
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_delete_copy(client):
    book = await client.post("/api/v1/books/", json={"title": "Del Copy Book"})
    book_id = book.json()["id"]
    copy = await client.post(f"/api/v1/books/{book_id}/copies")
    copy_id = copy.json()["id"]
    response = await client.delete(f"/api/v1/copies/{copy_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_create_copy_book_not_found(client):
    response = await client.post("/api/v1/books/99999/copies")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_copies_book_not_found(client):
    response = await client.get("/api/v1/books/99999/copies")
    assert response.status_code == 404
