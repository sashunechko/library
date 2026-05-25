import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Table, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


book_authors = Table(
    "book_authors",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id", ondelete="CASCADE"), primary_key=True),
    Column("author_id", Integer, ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True),
)


class CopyStatus(str, enum.Enum):
    available = "available"
    borrowed = "borrowed"


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    bio: Mapped[str | None] = mapped_column(Text)

    books: Mapped[list["Book"]] = relationship(secondary=book_authors, back_populates="authors")


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    isbn: Mapped[str | None] = mapped_column(String(13), unique=True)
    year: Mapped[int | None] = mapped_column(Integer)

    authors: Mapped[list["Author"]] = relationship(secondary=book_authors, back_populates="books", lazy="selectin")
    copies: Mapped[list["Copy"]] = relationship(back_populates="book", passive_deletes=True)


class Copy(Base):
    __tablename__ = "copies"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"))
    status: Mapped[CopyStatus] = mapped_column(Enum(CopyStatus), default=CopyStatus.available)

    book: Mapped["Book"] = relationship(back_populates="copies")


class Reader(Base):
    __tablename__ = "readers"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)

    loans: Mapped[list["Loan"]] = relationship(back_populates="reader", passive_deletes=True)


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True)
    copy_id: Mapped[int] = mapped_column(ForeignKey("copies.id", ondelete="CASCADE"))
    reader_id: Mapped[int] = mapped_column(ForeignKey("readers.id", ondelete="CASCADE"))
    loan_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    return_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    copy: Mapped["Copy"] = relationship()
    reader: Mapped["Reader"] = relationship(back_populates="loans")
