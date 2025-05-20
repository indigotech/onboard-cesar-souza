import pytest
import pytest_asyncio
import bcrypt
from datetime import date
from app.models import User

@pytest_asyncio.fixture
async def create_users(async_session):
    async def _create_users(count: int):
        users = []
        for i in range(count):
            name = f"user{i}"
            email = f"user{i}@test.com"
            birth_date = date(1999, 5, 10)
            hashed = bcrypt.hashpw("abcd1234".encode(), bcrypt.gensalt()).decode()
            user = User(name=name, email=email, password=hashed, birthDate=birth_date)
            async_session.add(user)
            users.append(user)
        await async_session.commit()
        for user in users:
            await async_session.refresh(user)
        return users
    return _create_users

def user_response(users):
    return sorted(
        [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "birthDate": user.birthDate.isoformat()
            }
            for user in users
        ],
        key=lambda x: x["name"]
    )

@pytest.mark.asyncio
async def test_list_users_no_users(client, auth_header):
    response = await client.get("/users", headers=auth_header)
    assert response.status_code == 200
    assert response.json() == {
        "users": [],
        "total": 0,
        "has_prev": False,
        "has_next": False
    }

@pytest.mark.asyncio
async def test_list_users_less_than_limit(client, create_users, auth_header):
    created_users = await create_users(5)
    response = await client.get("/users", headers=auth_header)
    assert response.status_code == 200
    expected_users = user_response(created_users)
    assert response.json() == {
        "users": expected_users,
        "total": 5,
        "has_prev": False,
        "has_next": False
    }

@pytest.mark.asyncio
async def test_list_users_with_skip(client, create_users, auth_header):
    created_users = await create_users(10)
    response = await client.get("/users?skip=5", headers=auth_header)
    assert response.status_code == 200
    
    expected_users = user_response(created_users[5:])
    assert response.json() == {
        "users": expected_users,
        "total": 10,
        "has_prev": True,
        "has_next": False
    }
 
@pytest.mark.asyncio
async def test_list_users_limit_less_than_total(client, create_users, auth_header):
    created_users = await create_users(10)
    response = await client.get("/users?limit=3", headers=auth_header)
    assert response.status_code == 200
    
    expected_users = user_response(created_users[:3])
    assert response.json() == {
        "users": expected_users,
        "total": 10,
        "has_prev": False,
        "has_next": True
    }
