from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel

from app.models import CopyStatus


# --- Authors ---

class AuthorCreate(BaseModel):
    first_name: str
    last_name: str
    bio: str | None = None


class AuthorUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    bio: str | None = None


class AuthorRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    bio: str | None

    model_config = {"from_attributes": True}


# --- Books ---

class BookCreate(BaseModel):
    title: str
    description: str | None = None
    isbn: str | None = None
    year: int | None = None
    author_ids: list[int] = []


class BookUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    isbn: str | None = None
    year: int | None = None
    author_ids: list[int] | None = None


class BookRead(BaseModel):
    id: int
    title: str
    description: str | None
    isbn: str | None
    year: int | None
    authors: list[AuthorRead] = []

    model_config = {"from_attributes": True}


# --- Copies ---

class CopyRead(BaseModel):
    id: int
    book_id: int
    status: CopyStatus

    model_config = {"from_attributes": True}


# --- Readers ---

class ReaderCreate(BaseModel):
    first_name: str
    last_name: str
    email: str


class ReaderUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None


class ReaderRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str

    model_config = {"from_attributes": True}


# --- Loans ---

class LoanCreate(BaseModel):
    copy_id: int
    reader_id: int


class LoanRead(BaseModel):
    id: int
    copy_id: int
    reader_id: int
    loan_date: datetime
    return_date: datetime | None

    model_config = {"from_attributes": True}


# --- Pagination ---

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    offset: int
    limit: int
