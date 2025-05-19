from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models, schemas
from .exceptions import AppError
import re
import bcrypt
from .jwt import create_access_token

PASSWORD_VALIDATION_REGEX = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$'

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    if len(user.name) < 3:
        raise AppError(
            status_code=400,
            code="USR_01",
            message="Nome deve ter pelo menos 3 caracteres.",
            details="Name must be at least 3 characters long"
        )

    result = await db.execute(select(models.User).where(models.User.email == user.email))
    if result.scalar_one_or_none():
        raise AppError(
            status_code=400,
            code="USR_02",
            message="E-mail já cadastrado.",
            details="A user with this email already exists"
        )

    if not re.search(PASSWORD_VALIDATION_REGEX, user.password):
        raise AppError(
            status_code=400,
            code="USR_03",
            message="Credenciais inválidas. Por favor, reveja.",
            details="Password must be at least 6 characters long and contain at least one letter and one number"
        )

    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

    db_user = models.User(
        name=user.name,
        email=user.email,
        password=hashed_password.decode('utf-8'),
        birthDate=user.birthDate
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def authenticate(db: AsyncSession, auth: schemas.AuthRequest) -> tuple[models.User, str]:
    result = await db.execute(select(models.User).where(models.User.email == auth.email))
    user = result.scalar_one_or_none()
    if not user:
        raise AppError(
            status_code=400,
            code="AUTH_01",
            message="Usuário não encontrado.",
            details="User not found"
        )

    if not bcrypt.checkpw(auth.password.encode('utf-8'), user.password.encode('utf-8')):
        raise AppError(
            status_code=401,
            code="AUTH_02",
            message="Senha incorreta.",
            details="Incorrect password"
        )
    
    token = create_access_token(
        user_id=int(user.id),
        remember_me=bool(auth.rememberMe)
    )
    return user, token

async def get_user(db: AsyncSession, id: int):
    result = await db.execute(select(models.User).where(models.User.id == id))
    user = result.scalar_one_or_none()
    if not user:
        raise AppError(
            status_code=404,
            code="AUTH_01",
            message="Usuário não encontrado.",
            details="User not found"
        )
    return user

async def list_users(db: AsyncSession, max_number: int | None = None) -> list[models.User]:
    limit = max_number or 10
    result = await db.execute(select(models.User).order_by(models.User.name).limit(limit))
    users = list(result.scalars().all())
    if not users:
        raise AppError(
            status_code=404,
            code="AUTH_01",
            message="Nenhum usuário encontrado.",
            details="User not found"
        )
    return users
