import jwt
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, UTC

load_dotenv()

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]
DEFAULT_EXP_MINUTES = 15
REMEMBER_ME_EXP_DAYS = 7

def create_access_token(user_id: int, remember_me: bool) -> str:
    expire = datetime.now(UTC) + (
        timedelta(days=REMEMBER_ME_EXP_DAYS) if remember_me else timedelta(minutes=DEFAULT_EXP_MINUTES)
    )
    payload = {
        "sub": str(user_id),
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
