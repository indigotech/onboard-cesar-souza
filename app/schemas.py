from pydantic import BaseModel
from datetime import date

class UserBase(BaseModel):
    name: str
    email: str
    birthDate: date

class Address(BaseModel):
    id: int
    cep: str
    street: str
    street_number: str
    complement: str
    neighborhood: str
    city: str
    state: str
    user_id: int

class UserCreate(UserBase):
    password: str

class User(BaseModel):
    id: int
    name: str
    email: str
    birthDate: date
    addresses: list[Address]

    class Config:
        from_attributes = True

class AuthRequest(BaseModel):
    email: str
    password: str
    rememberMe: bool = False

class AuthResponse(BaseModel):
    user: User
    token: str

class PaginatedUsers(BaseModel):
    users: list[User]
    total: int
    has_prev: bool
    has_next: bool
