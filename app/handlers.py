from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from .exceptions import AppError

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())
