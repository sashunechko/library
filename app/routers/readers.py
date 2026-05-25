from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import create_reader, delete_reader, get_reader, get_readers, update_reader
from app.database import get_db
from app.schemas import PaginatedResponse, ReaderCreate, ReaderRead, ReaderUpdate

router = APIRouter(prefix="/readers", tags=["readers"])


@router.get("/", response_model=PaginatedResponse[ReaderRead])
async def list_readers(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    items, total = await get_readers(db, offset, limit)
    return {"items": items, "total": total, "offset": offset, "limit": limit}


@router.get("/{reader_id}", response_model=ReaderRead)
async def read_reader(reader_id: int, db: AsyncSession = Depends(get_db)):
    reader = await get_reader(db, reader_id)
    if reader is None:
        raise HTTPException(status_code=404, detail="Reader not found")
    return reader


@router.post("/", response_model=ReaderRead, status_code=201)
async def create_reader_endpoint(reader: ReaderCreate, db: AsyncSession = Depends(get_db)):
    return await create_reader(db, reader)


@router.put("/{reader_id}", response_model=ReaderRead)
async def update_reader_endpoint(reader_id: int, reader: ReaderUpdate, db: AsyncSession = Depends(get_db)):
    db_reader = await get_reader(db, reader_id)
    if db_reader is None:
        raise HTTPException(status_code=404, detail="Reader not found")
    return await update_reader(db, db_reader, reader)


@router.delete("/{reader_id}", status_code=204)
async def delete_reader_endpoint(reader_id: int, db: AsyncSession = Depends(get_db)):
    db_reader = await get_reader(db, reader_id)
    if db_reader is None:
        raise HTTPException(status_code=404, detail="Reader not found")
    await delete_reader(db, db_reader)
