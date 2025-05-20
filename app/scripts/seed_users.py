import asyncio
import bcrypt
import os
import logging
from app.models import User
from faker import Faker
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.exceptions import AppError

fake = Faker()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_async_engine(DATABASE_URL)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def create_fake_users(n: int) -> list[User]:
    users = []
    for _ in range(n):
        name = fake.name()
        email = fake.unique.email()
        password = bcrypt.hashpw("test1234".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        birth_date = fake.date_of_birth(minimum_age=18, maximum_age=90)

        users.append(User(
            name=name,
            email=email,
            password=password,
            birthDate=birth_date
        ))
    return users

async def seed_users(n: int = 50) -> None:
    async with async_session() as session:
        try:
            logger.info(f"Criando {n} usuários...")
            users = await create_fake_users(n)
            session.add_all(users)
            await session.commit()
            logger.info(f"{n} usuários criados com sucesso.")
        except Exception as e:
            await session.rollback()
            raise AppError(
                status_code=500,
                code="SEED_01",
                message="Erro ao criar usuários.",
                details=str(e)
            )

def main() -> None:
    asyncio.run(seed_users())

if __name__ == "__main__":
    main()
