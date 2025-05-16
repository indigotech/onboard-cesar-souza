import os
from dotenv import load_dotenv
import pytest_asyncio
import bcrypt

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.database import get_db, Base
from app.models import User
from datetime import date

load_dotenv("test.env", override=True)

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    poolclass=NullPool
)
SessionTest = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client():
    async def override_get_db():
        async with SessionTest() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
        app.dependency_overrides.pop(get_db, None)

@pytest_asyncio.fixture
async def test_user():
    async with SessionTest() as session:
        user = User(
            name="tester",
            email="tester@test.com",
            password=bcrypt.hashpw("abcd1234".encode(), bcrypt.gensalt()).decode('utf-8'),
            birthDate=date(1999, 5, 9)
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
