import pytest
import bcrypt
from datetime import date
from sqlalchemy.future import select
from app.models import User
from .conftest import SessionTest

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
async def test_create_user_success(client):
    response = await client.post("/users/", json=BASE_PAYLOAD)
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
async def test_create_user_name_too_short(client):
    payload = {**BASE_PAYLOAD, "name": "ab"}
    response = await client.post("/users/", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "USR_01"
    assert data["message"] == "Nome deve ter pelo menos 3 caracteres."
    assert data["details"] == "Name must be at least 3 characters long"

@pytest.mark.asyncio
async def test_create_user_duplicate_email(client):
    await client.post("/users/", json=BASE_PAYLOAD)
    response = await client.post("/users/", json={**BASE_PAYLOAD})
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "USR_02"
    assert data["message"] == "E-mail já cadastrado."
    assert data["details"] == "A user with this email already exists"

@pytest.mark.asyncio
async def test_create_user_weak_password(client):
    payload = {**BASE_PAYLOAD, "password": "a1"}
    response = await client.post("/users/", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "USR_03"
    assert data["message"] == "Credenciais inválidas. Por favor, reveja."
    assert data["details"] == "Password must be at least 6 characters long and contain at least one letter and one number"
