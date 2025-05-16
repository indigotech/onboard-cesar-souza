import pytest
import bcrypt
import jwt
from datetime import date
from sqlalchemy.future import select
from app.models import User
from .conftest import SessionTest
from datetime import timedelta, datetime, UTC
from app.jwt import SECRET_KEY, ALGORITHM

BASE_PAYLOAD = {
    "name": "tester",
    "email": "tester@test.com",
    "password": "abcd1234",
    "birthDate": str(date(1999, 5, 9))
}

def user_response(user_id: int):
    return {
        "id": user_id,
        "name": BASE_PAYLOAD["name"],
        "email": BASE_PAYLOAD["email"],
        "birthDate": BASE_PAYLOAD["birthDate"],
    }

@pytest.mark.asyncio
async def test_create_user_success(client, auth_header):
    response = await client.post("/users", json=BASE_PAYLOAD, headers=auth_header)
    assert response.status_code == 201
    data = response.json()
    assert data == user_response(data["id"])
    async with SessionTest() as session:
        result = await session.execute(select(User).where(User.id == data["id"]))
        user = result.scalar_one()
        assert user.name == BASE_PAYLOAD["name"]
        assert user.email == BASE_PAYLOAD["email"]
        assert bcrypt.checkpw(BASE_PAYLOAD["password"].encode(), user.password.encode())
        assert user.birthDate.isoformat() == BASE_PAYLOAD["birthDate"]

@pytest.mark.asyncio
async def test_create_user_name_too_short(client, auth_header):
    payload = {**BASE_PAYLOAD, "name": "ab"}
    response = await client.post("/users", json=payload, headers=auth_header)
    assert response.status_code == 400
    assert response.json() == {
        "code": "USR_01",
        "message": "Nome deve ter pelo menos 3 caracteres.",
        "details": "Name must be at least 3 characters long"
    }

@pytest.mark.asyncio
async def test_create_user_duplicate_email(client, auth_header):
    await client.post("/users", json=BASE_PAYLOAD, headers=auth_header)
    response = await client.post("/users", json={**BASE_PAYLOAD}, headers=auth_header)
    assert response.status_code == 400
    assert response.json() == {
        "code": "USR_02",
        "message": "E-mail já cadastrado.",
        "details": "A user with this email already exists"
    }

@pytest.mark.asyncio
async def test_create_user_weak_password(client, auth_header):
    payload = {**BASE_PAYLOAD, "password": "a1"}
    response = await client.post("/users", json=payload, headers=auth_header)
    assert response.status_code == 400
    assert response.json() == {
        "code": "USR_03",
        "message": "Credenciais inválidas. Por favor, reveja.",
        "details": "Password must be at least 6 characters long and contain at least one letter and one number"
    }

@pytest.mark.asyncio
async def test_create_user_unauthenticated(client):
    response = await client.post("/users", json=BASE_PAYLOAD)
    assert response.status_code == 401
    assert response.json() == {
        "code": "AUTH_03",
        "message": "Autenticação necessária.",
        "details": "Authorization header missing or not Bearer"
    }

@pytest.mark.asyncio
async def test_create_user_token_expired(client):
    expired_time = datetime.now(UTC) - timedelta(minutes=1)
    token = jwt.encode({"sub": "123", "exp": expired_time}, SECRET_KEY, algorithm=ALGORITHM)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post("/users", json=BASE_PAYLOAD, headers=headers)
    assert response.status_code == 401
    assert response.json() == {
        "code": "AUTH_04",
        "message": "Token expirado.",
        "details": "Authentication token has expired"
    }

@pytest.mark.asyncio
async def test_create_user_invalid_token(client):
    valid_time = datetime.now(UTC) + timedelta(minutes=15)
    invalid_token = jwt.encode({"sub": "123", "exp": valid_time}, "wrong-secret", algorithm=ALGORITHM)
    headers = {"Authorization": f"Bearer {invalid_token}"}
    response = await client.post("/users", json=BASE_PAYLOAD, headers=headers)
    assert response.status_code == 401
    assert response.json() == {
        "code": "AUTH_05",
        "message": "Token inválido.",
        "details": "Could not validate credentials"
    }

@pytest.mark.asyncio
async def test_create_user_missing_sub(client):
    valid_time = datetime.now(UTC) + timedelta(minutes=15)
    token = jwt.encode({"exp": valid_time}, SECRET_KEY, algorithm=ALGORITHM)
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post("/users", json=BASE_PAYLOAD, headers=headers)
    assert response.status_code == 401
    assert response.json() == {
        "code": "AUTH_06",
        "message": "Payload de token inválido.",
        "details": "Missing subject"
    }
