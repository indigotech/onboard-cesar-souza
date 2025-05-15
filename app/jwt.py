import jwt
import os
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from dotenv import load_dotenv
from datetime import datetime, timedelta, UTC
from .exceptions import AppError

load_dotenv()

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]
DEFAULT_EXP_MINUTES = float(os.environ["DEFAULT_EXP"])
REMEMBER_ME_EXP_DAYS = float(os.environ["REMEMBER_ME_EXP"])

security = HTTPBearer(auto_error=False)

def create_access_token(user_id: int, remember_me: bool) -> str:
    expire = datetime.now(UTC) + (
        timedelta(days=REMEMBER_ME_EXP_DAYS) if remember_me else timedelta(minutes=DEFAULT_EXP_MINUTES)
    )
    payload = {
        "sub": str(user_id),
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise AppError(
            status_code=401,
            code="AUTH_04",
            message="Token expirado.",
            details="Authentication token has expired"
        )
    except jwt.InvalidTokenError:
        raise AppError(
            status_code=401,
            code="AUTH_05",
            message="Token inválido.",
            details="Could not validate credentials"
        )
    if "sub" not in payload:
        raise AppError(
            status_code=401,
            code="AUTH_06",
            message="Payload de token inválido.",
            details="Missing subject"
        )
    return payload

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise AppError(
            status_code=401,
            code="AUTH_03",
            message="Autenticação necessária.",
            details="Authorization header missing or not Bearer"
        )
    return decode_access_token(credentials.credentials)
