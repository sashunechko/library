from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import LoanError, create_loan, get_loan, get_loans, return_loan
from app.database import get_db
from app.schemas import LoanCreate, LoanRead, PaginatedResponse

router = APIRouter(prefix="/loans", tags=["loans"])


@router.get("/", response_model=PaginatedResponse[LoanRead])
async def list_loans(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    reader_id: int | None = None,
    copy_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    items, total = await get_loans(db, offset, limit, reader_id, copy_id)
    return {"items": items, "total": total, "offset": offset, "limit": limit}


@router.get("/{loan_id}", response_model=LoanRead)
async def read_loan(loan_id: int, db: AsyncSession = Depends(get_db)):
    loan = await get_loan(db, loan_id)
    if loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan


@router.post("/", response_model=LoanRead, status_code=201)
async def create_loan_endpoint(loan: LoanCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await create_loan(db, loan)
    except LoanError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{loan_id}/return", response_model=LoanRead)
async def return_loan_endpoint(loan_id: int, db: AsyncSession = Depends(get_db)):
    loan = await get_loan(db, loan_id)
    if loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    if loan.return_date is not None:
        raise HTTPException(status_code=400, detail="Book already returned")
    return await return_loan(db, loan)
