import pytest
import jwt
import os
from datetime import date, datetime, timezone

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]

BASE_PAYLOAD = {
    "name": "tester",
    "email": "tester@test.com",
    "password": "abcd1234",
    "birthDate": str(date(1999, 5, 9))
}

AUTH_PAYLOAD = {
    "email": BASE_PAYLOAD["email"],
    "password": "abcd1234",
}

def user_response(user_id: int, token: str):
    return {
        "user": {
            "id": user_id,
            "name": BASE_PAYLOAD["name"],
            "email": BASE_PAYLOAD["email"],
            "birthDate": BASE_PAYLOAD["birthDate"],
        },
        "token": token
    }

@pytest.mark.asyncio
async def test_authenticate_success(client):
    create_response = await client.post("/users", json=BASE_PAYLOAD)
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]

    auth_response = await client.post("/auth", json=AUTH_PAYLOAD)
    assert auth_response.status_code == 200

    data = auth_response.json()
    token = data["token"]
    assert isinstance(token, str)

    assert data == user_response(user_id, token)

    payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
    assert payload["sub"] == str(user_id)
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
async def test_authenticate_invalid_password(client):
    create_response = await client.post("/users", json=BASE_PAYLOAD)
    assert create_response.status_code == 201
    payload = {**AUTH_PAYLOAD, "password": "wrongpassword"}
    response = await client.post("/auth", json=payload)
    assert response.status_code == 401
    assert response.json() == {
        "code": "AUTH_02",
        "message": "Senha incorreta.",
        "details": "Incorrect password"
    }

@pytest.mark.asyncio
async def test_authenticate_with_remember_me(client):
    create_response = await client.post("/users", json=BASE_PAYLOAD)
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]

    payload = {**AUTH_PAYLOAD, "rememberMe": True}
    auth_response = await client.post("/auth", json=payload)
    assert auth_response.status_code == 200

    data = auth_response.json()
    token = data["token"]
    assert isinstance(token, str)

    assert data == user_response(user_id, token)

    payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
    assert payload["sub"] == str(user_id)
    assert isinstance(payload["exp"], int)

    exp_dt = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    now = datetime.now(timezone.utc)
    delta = exp_dt - now
    assert delta.days >= 6
