import os
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import get_db, settings
from app.main import app
from app.models import Base


def _resolve_test_db_url() -> str:
    url = os.getenv("TEST_DATABASE_URL")
    if url:
        return url
    base = settings.database_url
    # подменяем имя БД на library_test, чтобы случайно не зашибить прод-данные
    if "/library" in base and not base.endswith("_test"):
        return base.replace("/library", "/library_test")
    return base + "_test"


TEST_DATABASE_URL = _resolve_test_db_url()


async def _ensure_test_database() -> None:
    """Создаёт тестовую БД, если её ещё нет.

    Работает в обход того, что docker-entrypoint-initdb.d может не отработать
    на уже существующем volume.
    """
    admin_url, _, db_name = TEST_DATABASE_URL.rpartition("/")
    admin_url = f"{admin_url}/postgres"
    admin_engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        async with admin_engine.connect() as conn:
            exists = await conn.scalar(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": db_name},
            )
            if not exists:
                await conn.execute(text(f'CREATE DATABASE "{db_name}"'))
    finally:
        await admin_engine.dispose()


test_engine = create_async_engine(TEST_DATABASE_URL)
test_session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    await _ensure_test_database()
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
