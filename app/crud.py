from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Author, Book, Copy, CopyStatus, Loan, Reader
from app.schemas import (
    AuthorCreate,
    AuthorUpdate,
    BookCreate,
    BookUpdate,
    LoanCreate,
    ReaderCreate,
    ReaderUpdate,
)


class LoanError(Exception):
    """Доменная ошибка для операций над выдачами (роутер маппит в 400)."""


# --- Authors ---

async def get_authors(db: AsyncSession, offset: int = 0, limit: int = 10) -> tuple[list[Author], int]:
    total = (await db.execute(select(func.count(Author.id)))).scalar_one()
    result = await db.execute(select(Author).order_by(Author.id).offset(offset).limit(limit))
    return list(result.scalars().all()), total


async def get_author(db: AsyncSession, author_id: int) -> Author | None:
    return await db.get(Author, author_id)


async def create_author(db: AsyncSession, data: AuthorCreate) -> Author:
    author = Author(**data.model_dump())
    db.add(author)
    await db.flush()
    return author


async def update_author(db: AsyncSession, author: Author, data: AuthorUpdate) -> Author:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(author, field, value)
    await db.flush()
    return author


async def delete_author(db: AsyncSession, author: Author) -> None:
    await db.delete(author)
    await db.flush()


# --- Books ---

async def _load_authors(db: AsyncSession, author_ids: list[int]) -> list[Author]:
    if not author_ids:
        return []
    result = await db.execute(select(Author).where(Author.id.in_(author_ids)))
    return list(result.scalars().all())


async def get_books(
    db: AsyncSession,
    offset: int = 0,
    limit: int = 10,
    author_id: int | None = None,
) -> tuple[list[Book], int]:
    query = select(Book).order_by(Book.id)
    count_query = select(func.count(Book.id))
    if author_id is not None:
        query = query.join(Book.authors).where(Author.id == author_id)
        count_query = count_query.join(Book.authors).where(Author.id == author_id)

    total = (await db.execute(count_query)).scalar_one()
    result = await db.execute(query.offset(offset).limit(limit))
    return list(result.scalars().unique().all()), total


async def get_book(db: AsyncSession, book_id: int) -> Book | None:
    return await db.get(Book, book_id)


async def create_book(db: AsyncSession, data: BookCreate) -> Book:
    book = Book(
        title=data.title,
        description=data.description,
        isbn=data.isbn,
        year=data.year,
    )
    book.authors = await _load_authors(db, data.author_ids)
    db.add(book)
    await db.flush()
    await db.refresh(book, ["authors"])
    return book


async def update_book(db: AsyncSession, book: Book, data: BookUpdate) -> Book:
    payload = data.model_dump(exclude_unset=True)
    author_ids = payload.pop("author_ids", None)

    for field, value in payload.items():
        setattr(book, field, value)

    if author_ids is not None:
        book.authors = await _load_authors(db, author_ids)

    await db.flush()
    await db.refresh(book, ["authors"])
    return book


async def delete_book(db: AsyncSession, book: Book) -> None:
    await db.delete(book)
    await db.flush()


# --- Copies ---

async def get_copies(db: AsyncSession, book_id: int) -> list[Copy]:
    result = await db.execute(
        select(Copy).where(Copy.book_id == book_id).order_by(Copy.id)
    )
    return list(result.scalars().all())


async def get_copy(db: AsyncSession, copy_id: int) -> Copy | None:
    return await db.get(Copy, copy_id)


async def create_copy(db: AsyncSession, book_id: int) -> Copy:
    copy = Copy(book_id=book_id)
    db.add(copy)
    await db.flush()
    return copy


async def delete_copy(db: AsyncSession, copy: Copy) -> None:
    await db.delete(copy)
    await db.flush()


# --- Readers ---

async def get_readers(db: AsyncSession, offset: int = 0, limit: int = 10) -> tuple[list[Reader], int]:
    total = (await db.execute(select(func.count(Reader.id)))).scalar_one()
    result = await db.execute(select(Reader).order_by(Reader.id).offset(offset).limit(limit))
    return list(result.scalars().all()), total


async def get_reader(db: AsyncSession, reader_id: int) -> Reader | None:
    return await db.get(Reader, reader_id)


async def create_reader(db: AsyncSession, data: ReaderCreate) -> Reader:
    reader = Reader(**data.model_dump())
    db.add(reader)
    await db.flush()
    return reader


async def update_reader(db: AsyncSession, reader: Reader, data: ReaderUpdate) -> Reader:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(reader, field, value)
    await db.flush()
    return reader


async def delete_reader(db: AsyncSession, reader: Reader) -> None:
    await db.delete(reader)
    await db.flush()


# --- Loans ---

async def get_loans(
    db: AsyncSession,
    offset: int = 0,
    limit: int = 10,
    reader_id: int | None = None,
    copy_id: int | None = None,
) -> tuple[list[Loan], int]:
    query = select(Loan).order_by(Loan.id)
    count_query = select(func.count(Loan.id))
    if reader_id is not None:
        query = query.where(Loan.reader_id == reader_id)
        count_query = count_query.where(Loan.reader_id == reader_id)
    if copy_id is not None:
        query = query.where(Loan.copy_id == copy_id)
        count_query = count_query.where(Loan.copy_id == copy_id)

    total = (await db.execute(count_query)).scalar_one()
    result = await db.execute(query.offset(offset).limit(limit))
    return list(result.scalars().all()), total


async def get_loan(db: AsyncSession, loan_id: int) -> Loan | None:
    return await db.get(Loan, loan_id)


async def create_loan(db: AsyncSession, data: LoanCreate) -> Loan:
    copy = await db.get(Copy, data.copy_id)
    if copy is None:
        raise LoanError("Copy not found")
    if copy.status != CopyStatus.available:
        raise LoanError("Copy is not available")

    reader = await db.get(Reader, data.reader_id)
    if reader is None:
        raise LoanError("Reader not found")

    copy.status = CopyStatus.borrowed
    loan = Loan(copy_id=data.copy_id, reader_id=data.reader_id)
    db.add(loan)
    await db.flush()
    await db.refresh(loan)
    return loan


async def return_loan(db: AsyncSession, loan: Loan) -> Loan:
    copy = await db.get(Copy, loan.copy_id)
    if copy is not None:
        copy.status = CopyStatus.available
    loan.return_date = datetime.now(timezone.utc)
    await db.flush()
    return loan
