import pytest
import pytest_asyncio
import bcrypt
from datetime import date
from app.models import User

@pytest_asyncio.fixture
async def create_user(async_session):
    async def _create_user(
        name: str = "tester",
        email: str = "tester@test.com",
        password: str = "abcd1234",
        birth_date: date = date(1999, 5, 9)
    ):
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')
        user = User(name=name, email=email, password=hashed, birthDate=birth_date)
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)
        return user
    return _create_user

@pytest.mark.asyncio
async def test_get_user_success(client, create_user, auth_header):
    user = await create_user()
    response = await client.get(f"/user/{user.id}", headers=auth_header)
    assert response.status_code == 200
    assert response.json() == {
        "id": user.id,
        "name": "tester",
        "email": "tester@test.com",
        "birthDate": "1999-05-09"
    }

@pytest.mark.asyncio
async def test_get_user_not_found(client, auth_header):
    response = await client.get("/user/999", headers=auth_header)
    assert response.status_code == 404
    assert response.json() == {
        "code": "AUTH_01",
        "message": "Usuário não encontrado.",
        "details": "User not found"
    }

@pytest.mark.asyncio
async def test_get_user_unauthenticated(client, create_user):
    user = await create_user() 
    response = await client.get(f"/user/{user.id}")
    assert response.status_code == 401
    assert response.json() == {
        "code": "AUTH_03",
        "message": "Autenticação necessária.",
        "details": "Authorization header missing or not Bearer"
    }
