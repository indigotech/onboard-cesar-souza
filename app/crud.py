from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models, schemas
from .exceptions import UserNameTooShortError, EmailAlreadyExistsError, WeakPasswordError
import re
import bcrypt

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    if len(user.name) < 3:
        raise UserNameTooShortError()

    result = await db.execute(select(models.User).where(models.User.email == user.email))
    if result.scalar_one_or_none():
        raise EmailAlreadyExistsError()

    PASSWORD_VALIDATION_REGEX = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$'
    if not re.search(PASSWORD_VALIDATION_REGEX, user.password):
        raise WeakPasswordError()

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
