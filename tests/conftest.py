import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.database import get_db
from app.environment import settings
from app.main import app
from app.models import Base, User
from app.security import get_password_hash


@pytest.fixture(scope="function")
async def engine():
    engine = create_async_engine(
        settings.TEST_DB_URL.render_as_string(hide_password=False)
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        await conn.execute(
            insert(User)
            .values(
                username=settings.ADMIN_USER,
                email=settings.ADMIN_EMAIL,
                hashed_password=get_password_hash(settings.ADMIN_PASS),
                is_admin=True
            )
        )

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(engine):
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise


@pytest.fixture(scope="function")
async def test_client(db_session):
    async def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def admin_token(test_client: AsyncClient) -> str:
    response = await test_client.post("/login", data={
        "username": settings.ADMIN_EMAIL,
        "password": settings.ADMIN_PASS
    })
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
