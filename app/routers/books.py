from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import create_book, delete_book, get_book, get_books, update_book
from app.database import get_db
from app.schemas import BookCreate, BookRead, BookUpdate, PaginatedResponse

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=PaginatedResponse[BookRead])
async def list_books(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    author_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    items, total = await get_books(db, offset, limit, author_id)
    return {"items": items, "total": total, "offset": offset, "limit": limit}


@router.get("/{book_id}", response_model=BookRead)
async def read_book(book_id: int, db: AsyncSession = Depends(get_db)):
    book = await get_book(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/", response_model=BookRead, status_code=201)
async def create_book_endpoint(book: BookCreate, db: AsyncSession = Depends(get_db)):
    return await create_book(db, book)


@router.put("/{book_id}", response_model=BookRead)
async def update_book_endpoint(book_id: int, book: BookUpdate, db: AsyncSession = Depends(get_db)):
    db_book = await get_book(db, book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return await update_book(db, db_book, book)


@router.delete("/{book_id}", status_code=204)
async def delete_book_endpoint(book_id: int, db: AsyncSession = Depends(get_db)):
    db_book = await get_book(db, book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    await delete_book(db, db_book)
