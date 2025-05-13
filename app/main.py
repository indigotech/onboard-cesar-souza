from fastapi import FastAPI, Query, Depends, HTTPException, status
from pydantic import BaseModel
from . import models
from . import crud, models, schemas
from .database import engine, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from .handlers import register_exception_handlers

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    register_exception_handlers(app)
    yield

app = FastAPI(lifespan=lifespan)

class HelloResponse(BaseModel):
    message: str
    class Config():
        json_schema_extra = {
            "example": {
                "message": "Hello, Cesar"
            }
        }

@app.get("/hello", response_model=HelloResponse)
async def send_hello(name: str = Query(min_length=2)):
    return HelloResponse(message=f"Hello, {name}")

@app.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    result = await crud.create_user(db=db, user=user)
    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)
    return result
