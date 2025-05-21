import pytest
import pytest_asyncio
import jwt
import bcrypt
from datetime import date, datetime, timezone
from app.models import User
from app.jwt import SECRET_KEY, ALGORITHM

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

AUTH_PAYLOAD = {
    "email": "tester@test.com",
    "password": "abcd1234",
    "rememberMe": False
}

def user_response(user_id: int, token: str):
    return {
        "user": {
            "id": user_id,
            "name": "tester",
            "email": AUTH_PAYLOAD["email"],
            "birthDate": str(date(1999, 5, 9)),
            "addresses": []
        },
        "token": token
    }

@pytest.mark.asyncio
async def test_authenticate_success(client, create_user):
    user = await create_user()
    auth_response = await client.post("/auth", json=AUTH_PAYLOAD)
    assert auth_response.status_code == 200

    data = auth_response.json()
    token = data["token"]
    assert isinstance(token, str)

    assert data == user_response(user.id, token)

    payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
    assert payload["sub"] == str(user.id)
    assert isinstance(payload["exp"], int)

    exp_dt = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    now = datetime.now(timezone.utc)
    delta = exp_dt - now
    assert 14 <= delta.total_seconds() / 60 <= 16

@pytest.mark.asyncio
async def test_authenticate_invalid_email(client):
    payload = {**AUTH_PAYLOAD, "email": "test@test.com"}
    response = await client.post("/auth", json=payload)
    assert response.status_code == 400
    assert response.json() == {
        "code": "AUTH_01",
        "message": "Usuário não encontrado.",
        "details": "User not found"
    }

@pytest.mark.asyncio
async def test_authenticate_invalid_password(client, create_user):
    user = await create_user()
    payload = {**AUTH_PAYLOAD, "password": "wrongpassword"}
    response = await client.post("/auth", json=payload)
    assert response.status_code == 401
    assert response.json() == {
        "code": "AUTH_02",
        "message": "Senha incorreta.",
        "details": "Incorrect password"
    }

@pytest.mark.asyncio
async def test_authenticate_with_remember_me(client, create_user):
    user = await create_user()
    payload = {**AUTH_PAYLOAD, "rememberMe": True}
    auth_response = await client.post("/auth", json=payload)
    assert auth_response.status_code == 200

    data = auth_response.json()
    token = data["token"]
    assert isinstance(token, str)

    assert data == user_response(user.id, token)

    payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
    assert payload["sub"] == str(user.id)
    assert isinstance(payload["exp"], int)

    exp_dt = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    now = datetime.now(timezone.utc)
    delta = exp_dt - now
    assert delta.days >= 6
