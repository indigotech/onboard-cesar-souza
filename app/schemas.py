from pydantic import BaseModel
from datetime import date

class UserBase(BaseModel):
    name: str
    email: str
    birthDate: date

class UserCreate(UserBase):
    password: str

class User(BaseModel):
    id: int
    name: str
    email: str
    birthDate: date

    class Config:
        from_attributes = True
