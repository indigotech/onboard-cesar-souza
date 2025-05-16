import pytest

@pytest.mark.asyncio
async def test_get_user_success(client, test_user, auth_header):
    response = await client.get(f"/user/{test_user.id}", headers=auth_header)
    assert response.status_code == 200
    assert response.json() == {
        "id": test_user.id,
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
async def test_get_user_unauthenticated(client, test_user):
    response = await client.get(f"/user/{test_user.id}")
    assert response.status_code == 401
    assert response.json() == {
        "code": "AUTH_03",
        "message": "Autenticação necessária.",
        "details": "Authorization header missing or not Bearer"
    }
