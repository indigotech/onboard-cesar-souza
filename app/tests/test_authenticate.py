import pytest
import jwt
from datetime import date, datetime, timezone
from app.jwt import SECRET_KEY, ALGORITHM

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
            "birthDate": str(date(1999, 5, 9))
        },
        "token": token
    }

@pytest.mark.asyncio
async def test_authenticate_success(client, test_user):
    auth_response = await client.post("/auth", json=AUTH_PAYLOAD)
    assert auth_response.status_code == 200

    data = auth_response.json()
    token = data["token"]
    assert isinstance(token, str)

    assert data == user_response(test_user.id, token)

    payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
    assert payload["sub"] == str(test_user.id)
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
async def test_authenticate_invalid_password(client, test_user):
    payload = {**AUTH_PAYLOAD, "password": "wrongpassword"}
    response = await client.post("/auth", json=payload)
    assert response.status_code == 401
    assert response.json() == {
        "code": "AUTH_02",
        "message": "Senha incorreta.",
        "details": "Incorrect password"
    }

@pytest.mark.asyncio
async def test_authenticate_with_remember_me(client, test_user):
    payload = {**AUTH_PAYLOAD, "rememberMe": True}
    auth_response = await client.post("/auth", json=payload)
    assert auth_response.status_code == 200

    data = auth_response.json()
    token = data["token"]
    assert isinstance(token, str)

    assert data == user_response(test_user.id, token)

    payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
    assert payload["sub"] == str(test_user.id)
    assert isinstance(payload["exp"], int)

    exp_dt = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    now = datetime.now(timezone.utc)
    delta = exp_dt - now
    assert delta.days >= 6
