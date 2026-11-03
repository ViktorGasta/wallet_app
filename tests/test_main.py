import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    create_async_engine, async_sessionmaker, AsyncSession
)
from app.main import app
from app.database import get_db, Base

BASE_URL = "http://testserver/api/v1/wallets"

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(autouse=True, scope="function")
async def init_test_db():
    """Фикстура для создания таблиц в тестовой БД перед каждым тестом."""

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    """Замена оригинальной зависимости get_db на тестовую."""

    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

app.dependency_overrides[get_db] = override_get_db


@pytest.mark.asyncio
async def test_wallet_flow():
    fake_uuid = str(uuid.uuid4())
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        response = await ac.get(f"/{fake_uuid}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Wallet not found"

        payload = {"operation_type": "DEPOSIT", "amount": "1000.00"}
        response = await ac.post(f"/{fake_uuid}/operation", json=payload)
        assert response.status_code == 404
