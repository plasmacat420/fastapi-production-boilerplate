import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.database import get_db
from app.models.base import Base
from app.services.auth import create_token_pair
from app.services.user import create_user

TEST_DATABASE_URL = settings.TEST_DATABASE_URL


@pytest_asyncio.fixture(scope="session")
async def engine():
    eng = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture(autouse=True)
async def clean_tables(engine):
    """Delete all rows from every table after each test for isolation."""
    yield
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest_asyncio.fixture
async def db(engine):
    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def app(engine):
    from app.main import create_app

    _app = create_app()

    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    _app.dependency_overrides[get_db] = override_get_db
    return _app


@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def test_user(db):
    user = await create_user(
        db,
        email="user@example.com",
        password="password123",
        full_name="Test User",
        role="user",
    )
    await db.commit()
    return {"user": user, "password": "password123"}


@pytest_asyncio.fixture
async def test_admin(db):
    user = await create_user(
        db,
        email="admin@example.com",
        password="adminpass123",
        full_name="Admin User",
        role="admin",
    )
    await db.commit()
    return {"user": user, "password": "adminpass123"}


@pytest.fixture
def auth_headers(test_user):
    tokens = create_token_pair(str(test_user["user"].id), test_user["user"].role)
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture
def admin_headers(test_admin):
    tokens = create_token_pair(str(test_admin["user"].id), test_admin["user"].role)
    return {"Authorization": f"Bearer {tokens['access_token']}"}
