import pytest


@pytest.mark.asyncio
async def test_create_reader(client):
    response = await client.post("/api/v1/readers/", json={
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "email": "ivan@example.com",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "ivan@example.com"


@pytest.mark.asyncio
async def test_list_readers(client):
    response = await client.get("/api/v1/readers/")
    assert response.status_code == 200
    assert "items" in response.json()


@pytest.mark.asyncio
async def test_get_reader(client):
    create = await client.post("/api/v1/readers/", json={
        "first_name": "A", "last_name": "B", "email": "a@b.com",
    })
    reader_id = create.json()["id"]
    response = await client.get(f"/api/v1/readers/{reader_id}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_reader(client):
    create = await client.post("/api/v1/readers/", json={
        "first_name": "Old", "last_name": "Name", "email": "old@example.com",
    })
    reader_id = create.json()["id"]
    response = await client.put(f"/api/v1/readers/{reader_id}", json={"first_name": "New"})
    assert response.status_code == 200
    assert response.json()["first_name"] == "New"


@pytest.mark.asyncio
async def test_delete_reader(client):
    create = await client.post("/api/v1/readers/", json={
        "first_name": "Del", "last_name": "Me", "email": "del@example.com",
    })
    reader_id = create.json()["id"]
    response = await client.delete(f"/api/v1/readers/{reader_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_reader_with_active_loan(client):
    book = await client.post("/api/v1/books/", json={"title": "Cascade Book"})
    book_id = book.json()["id"]
    copy = await client.post(f"/api/v1/books/{book_id}/copies")
    copy_id = copy.json()["id"]
    reader = await client.post("/api/v1/readers/", json={
        "first_name": "Cascade", "last_name": "Reader", "email": "cascade@example.com",
    })
    reader_id = reader.json()["id"]
    await client.post("/api/v1/loans/", json={"copy_id": copy_id, "reader_id": reader_id})

    response = await client.delete(f"/api/v1/readers/{reader_id}")
    assert response.status_code == 204

    loans = await client.get(f"/api/v1/loans/?reader_id={reader_id}")
    assert loans.json()["total"] == 0


@pytest.mark.asyncio
async def test_duplicate_email(client):
    await client.post("/api/v1/readers/", json={
        "first_name": "A", "last_name": "B", "email": "dup@example.com",
    })
    response = await client.post("/api/v1/readers/", json={
        "first_name": "C", "last_name": "D", "email": "dup@example.com",
    })
    assert response.status_code == 409
