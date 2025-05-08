from pydantic import BaseModel
from datetime import date

class UserBase(BaseModel):
    name: str
    email: str
    password: str
    birthDate: date

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config:
        from_attributes = True
