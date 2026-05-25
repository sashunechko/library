"""Заполнение БД демо-данными.

Запуск:
    docker compose exec app python scripts/seed.py
или
    make seed

Скрипт идемпотентен — если в таблице authors уже есть записи, ничего не делает.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select, func

from app.database import async_session
from app.models import Author, Book, Copy, CopyStatus, Loan, Reader


AUTHORS = [
    {"first_name": "Лев", "last_name": "Толстой", "bio": "Русский писатель."},
    {"first_name": "Фёдор", "last_name": "Достоевский", "bio": "Русский писатель и философ."},
    {"first_name": "Антон", "last_name": "Чехов", "bio": "Драматург, врач."},
    {"first_name": "George", "last_name": "Orwell", "bio": "British novelist."},
]


BOOKS = [
    {"title": "Война и мир", "year": 1869, "isbn": "9785170902231", "author_idx": [0]},
    {"title": "Анна Каренина", "year": 1877, "isbn": "9785170902248", "author_idx": [0]},
    {"title": "Преступление и наказание", "year": 1866, "isbn": "9785170902255", "author_idx": [1]},
    {"title": "Идиот", "year": 1869, "isbn": "9785170902262", "author_idx": [1]},
    {"title": "Вишнёвый сад", "year": 1904, "isbn": "9785170902279", "author_idx": [2]},
    {"title": "1984", "year": 1949, "isbn": "9780451524935", "author_idx": [3]},
    {"title": "Animal Farm", "year": 1945, "isbn": "9780451526342", "author_idx": [3]},
]


READERS = [
    {"first_name": "Иван", "last_name": "Петров", "email": "ivan.petrov@example.com"},
    {"first_name": "Мария", "last_name": "Сидорова", "email": "maria.s@example.com"},
    {"first_name": "John", "last_name": "Doe", "email": "john.doe@example.com"},
]


async def seed() -> None:
    async with async_session() as session:
        existing = await session.scalar(select(func.count(Author.id)))
        if existing:
            print(f"в таблице authors уже {existing} записей — пропускаю seed")
            return

        authors = [Author(**a) for a in AUTHORS]
        session.add_all(authors)
        await session.flush()

        books: list[Book] = []
        for b in BOOKS:
            book = Book(title=b["title"], year=b["year"], isbn=b["isbn"])
            book.authors = [authors[i] for i in b["author_idx"]]
            books.append(book)
        session.add_all(books)
        await session.flush()

        # по 2 экземпляра на каждую книгу
        copies: list[Copy] = []
        for book in books:
            copies.append(Copy(book_id=book.id))
            copies.append(Copy(book_id=book.id))
        session.add_all(copies)
        await session.flush()

        readers = [Reader(**r) for r in READERS]
        session.add_all(readers)
        await session.flush()

        # одна активная выдача — чтобы было что показывать
        active_copy = copies[0]
        active_copy.status = CopyStatus.borrowed
        session.add(Loan(copy_id=active_copy.id, reader_id=readers[0].id))

        await session.commit()
        print(
            f"seed готов: {len(authors)} авторов, {len(books)} книг, "
            f"{len(copies)} экземпляров, {len(readers)} читателей, 1 активная выдача"
        )


if __name__ == "__main__":
    asyncio.run(seed())
