from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import create_author, delete_author, get_author, get_authors, update_author
from app.database import get_db
from app.schemas import AuthorCreate, AuthorRead, AuthorUpdate, PaginatedResponse

router = APIRouter(prefix="/authors", tags=["authors"])


@router.get("/", response_model=PaginatedResponse[AuthorRead])
async def list_authors(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    items, total = await get_authors(db, offset, limit)
    return {"items": items, "total": total, "offset": offset, "limit": limit}


@router.get("/{author_id}", response_model=AuthorRead)
async def read_author(author_id: int, db: AsyncSession = Depends(get_db)):
    author = await get_author(db, author_id)
    if author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@router.post("/", response_model=AuthorRead, status_code=201)
async def create_author_endpoint(author: AuthorCreate, db: AsyncSession = Depends(get_db)):
    return await create_author(db, author)


@router.put("/{author_id}", response_model=AuthorRead)
async def update_author_endpoint(author_id: int, author: AuthorUpdate, db: AsyncSession = Depends(get_db)):
    db_author = await get_author(db, author_id)
    if db_author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return await update_author(db, db_author, author)


@router.delete("/{author_id}", status_code=204)
async def delete_author_endpoint(author_id: int, db: AsyncSession = Depends(get_db)):
    db_author = await get_author(db, author_id)
    if db_author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    await delete_author(db, db_author)
