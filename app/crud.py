from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from . import models, schemas
import re

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    if len(user.name) < 3:
        raise HTTPException(status_code=400, detail="Name must be at least 3 characters long")
    
    result = await db.execute(select(models.User).where(models.User.email == user.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="A user with this email already exists")
    
    PASSWORD_VALIDATION_REGEX = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$'

    if not re.search(PASSWORD_VALIDATION_REGEX, user.password):
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long and contain at least one letter and one number")
    
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
