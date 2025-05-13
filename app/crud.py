from sqlalchemy.ext.asyncio import AsyncSession
from . import models, schemas

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    db_user = models.User(
        name=user.name,
        email=user.email,
        password=user.password,
        birthDate=user.birthDate
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
