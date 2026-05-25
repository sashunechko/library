import pytest


async def _create_book_with_copy(client):
    book = await client.post("/api/v1/books/", json={"title": "Loan Book"})
    book_id = book.json()["id"]
    copy = await client.post(f"/api/v1/books/{book_id}/copies")
    return copy.json()["id"]


async def _create_reader(client, email="loan@example.com"):
    reader = await client.post("/api/v1/readers/", json={
        "first_name": "R", "last_name": "D", "email": email,
    })
    return reader.json()["id"]


@pytest.mark.asyncio
async def test_issue_book(client):
    copy_id = await _create_book_with_copy(client)
    reader_id = await _create_reader(client)
    response = await client.post("/api/v1/loans/", json={
        "copy_id": copy_id, "reader_id": reader_id,
    })
    assert response.status_code == 201
    assert response.json()["return_date"] is None


@pytest.mark.asyncio
async def test_issue_borrowed_book_fails(client):
    copy_id = await _create_book_with_copy(client)
    reader_id = await _create_reader(client, "loan1@example.com")
    await client.post("/api/v1/loans/", json={"copy_id": copy_id, "reader_id": reader_id})
    reader2_id = await _create_reader(client, "loan2@example.com")
    response = await client.post("/api/v1/loans/", json={
        "copy_id": copy_id, "reader_id": reader2_id,
    })
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_return_book(client):
    copy_id = await _create_book_with_copy(client)
    reader_id = await _create_reader(client, "loan3@example.com")
    loan = await client.post("/api/v1/loans/", json={"copy_id": copy_id, "reader_id": reader_id})
    loan_id = loan.json()["id"]
    response = await client.post(f"/api/v1/loans/{loan_id}/return")
    assert response.status_code == 200
    assert response.json()["return_date"] is not None


@pytest.mark.asyncio
async def test_return_already_returned(client):
    copy_id = await _create_book_with_copy(client)
    reader_id = await _create_reader(client, "loan4@example.com")
    loan = await client.post("/api/v1/loans/", json={"copy_id": copy_id, "reader_id": reader_id})
    loan_id = loan.json()["id"]
    await client.post(f"/api/v1/loans/{loan_id}/return")
    response = await client.post(f"/api/v1/loans/{loan_id}/return")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_list_loans(client):
    response = await client.get("/api/v1/loans/")
    assert response.status_code == 200
    assert "items" in response.json()


@pytest.mark.asyncio
async def test_get_loan_not_found(client):
    response = await client.get("/api/v1/loans/99999")
    assert response.status_code == 404
