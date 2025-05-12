from fastapi import FastAPI, Query
from pydantic import BaseModel
from . import models
from .database import engine
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
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
