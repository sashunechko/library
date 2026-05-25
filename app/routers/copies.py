from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import create_copy, delete_copy, get_book, get_copy, get_copies
from app.database import get_db
from app.schemas import CopyRead

router = APIRouter(tags=["copies"])


@router.get("/books/{book_id}/copies", response_model=list[CopyRead])
async def list_copies(book_id: int, db: AsyncSession = Depends(get_db)):
    book = await get_book(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return await get_copies(db, book_id)


@router.post("/books/{book_id}/copies", response_model=CopyRead, status_code=201)
async def create_copy_endpoint(book_id: int, db: AsyncSession = Depends(get_db)):
    book = await get_book(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return await create_copy(db, book_id)


@router.delete("/copies/{copy_id}", status_code=204)
async def delete_copy_endpoint(copy_id: int, db: AsyncSession = Depends(get_db)):
    copy = await get_copy(db, copy_id)
    if copy is None:
        raise HTTPException(status_code=404, detail="Copy not found")
    await delete_copy(db, copy)
