import pytest
import pytest_asyncio
import bcrypt
from datetime import date
from app.models import User, Address

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

@pytest_asyncio.fixture
async def create_address(async_session):
    async def _create_address(
        user_id: int,
        cep: str,
        street: str,
        street_number: str,
        complement: str,
        neighborhood: str,
        city: str,
        state: str
    ) -> Address:
        addr = Address(
            user_id=user_id,
            cep=cep,
            street=street,
            street_number=street_number,
            complement=complement,
            neighborhood=neighborhood,
            city=city,
            state=state
        )
        async_session.add(addr)
        await async_session.commit()
        await async_session.refresh(addr)
        return addr
    return _create_address

def user_response(user, addresses):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "birthDate": user.birthDate.isoformat(),
        "addresses": [
            {
                "id": addr.id,
                "cep": addr.cep,
                "street": addr.street,
                "street_number": addr.street_number,
                "complement": addr.complement,
                "neighborhood": addr.neighborhood,
                "city": addr.city,
                "state": addr.state,
                "user_id": addr.user_id,
            }
            for addr in addresses
        ],
    }

@pytest.mark.asyncio
async def test_get_user_success(client, create_user, auth_header):
    user = await create_user()
    response = await client.get(f"/user/{user.id}", headers=auth_header)
    assert response.status_code == 200
    assert response.json() == {
        "id": user.id,
        "name": "tester",
        "email": "tester@test.com",
        "birthDate": "1999-05-09",
        "addresses": []
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

@pytest.mark.asyncio
async def test_get_user_with_addresses(client, create_user, create_address, auth_header):
    user = await create_user()
    addr1 = await create_address(
        user_id=user.id,
        cep="12345-678",
        street="Rua A",
        street_number="100",
        complement="Apto 10",
        neighborhood="Bairro X",
        city="Cidade Y",
        state="ST"
    )
    addr2 = await create_address(
        user_id=user.id,
        cep="87654-321",
        street="Avenida B",
        street_number="200",
        complement="Sala 5",
        neighborhood="Bairro Z",
        city="Cidade W",
        state="UV"
    )
    response = await client.get(f"/user/{user.id}", headers=auth_header)
    assert response.status_code == 200
    assert response.json() == user_response(user, [addr1, addr2])
