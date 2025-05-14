from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models, schemas
from .exceptions import AppError
import re
import bcrypt

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

    PASSWORD_VALIDATION_REGEX = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$'
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
