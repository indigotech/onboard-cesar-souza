from fastapi import FastAPI, Query, Path, Depends, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from . import models
from . import crud, models, schemas
from .database import engine, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from .exceptions import AppError
from .jwt import verify_token

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )

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

@app.post("/users", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db), _token_data: dict = Depends(verify_token)):
    result = await crud.create_user(db=db, user=user)
    if isinstance(result, str):
        raise AppError(
            status_code=400,
            code="USR_99",
            message="Erro ao criar usuário.",
            details=result
        )
    return result

@app.post("/auth", response_model=schemas.AuthResponse, status_code=status.HTTP_200_OK)
async def authenticate(auth: schemas.AuthRequest, db: AsyncSession = Depends(get_db)):
    result, token = await crud.authenticate(db=db, auth=auth)
    if isinstance(result, str):
        raise AppError(
            status_code=400,
            code="AUTH_99",
            message="Erro ao autenticar usuário.",
            details=result
        )
    return schemas.AuthResponse(
        user=schemas.User.model_validate(result),
        token=token
    )

@app.get("/user/{id}",response_model=schemas.User, status_code=status.HTTP_200_OK)
async def get_user(id: int = Path(title="User ID", gt=0), db:AsyncSession = Depends(get_db), _token_data: dict = Depends(verify_token)):
    result = await crud.get_user(db=db, id=id)
    return result

@app.get("/users",response_model=list[schemas.User], status_code=status.HTTP_200_OK)
async def list_users(max_number: int | None = Query(None, title="User listing limit", gt=0), db:AsyncSession = Depends(get_db), _token_data: dict = Depends(verify_token)):
    result = await crud.list_users(db=db, max_number=max_number)
    return result
