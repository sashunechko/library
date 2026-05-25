import pytest


@pytest.mark.asyncio
async def test_create_author(client):
    response = await client.post("/api/v1/authors/", json={
        "first_name": "Lev",
        "last_name": "Tolstoy",
        "bio": "Russian writer",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Lev"
    assert data["last_name"] == "Tolstoy"
    assert data["bio"] == "Russian writer"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_authors(client):
    await client.post("/api/v1/authors/", json={"first_name": "A", "last_name": "B"})
    response = await client.get("/api/v1/authors/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_get_author(client):
    create = await client.post("/api/v1/authors/", json={"first_name": "F", "last_name": "L"})
    author_id = create.json()["id"]
    response = await client.get(f"/api/v1/authors/{author_id}")
    assert response.status_code == 200
    assert response.json()["first_name"] == "F"


@pytest.mark.asyncio
async def test_get_author_not_found(client):
    response = await client.get("/api/v1/authors/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_author(client):
    create = await client.post("/api/v1/authors/", json={"first_name": "Old", "last_name": "Name"})
    author_id = create.json()["id"]
    response = await client.put(f"/api/v1/authors/{author_id}", json={"first_name": "New"})
    assert response.status_code == 200
    assert response.json()["first_name"] == "New"


@pytest.mark.asyncio
async def test_delete_author(client):
    create = await client.post("/api/v1/authors/", json={"first_name": "Del", "last_name": "Me"})
    author_id = create.json()["id"]
    response = await client.delete(f"/api/v1/authors/{author_id}")
    assert response.status_code == 204
    response = await client.get(f"/api/v1/authors/{author_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_author_missing_fields(client):
    response = await client.post("/api/v1/authors/", json={})
    assert response.status_code == 422
