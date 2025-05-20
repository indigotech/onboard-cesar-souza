from sqlalchemy import Column, Integer, String, Date, ForeignKey
from .database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, index=True)
    birthDate = Column(Date, index=True)
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")

class Address(Base):
    __tablename__ = "address"

    id = Column(Integer, primary_key=True, index=True)
    cep = Column(String)
    street = Column(String)
    street_number = Column(String)
    complement = Column(String)
    neighborhood = Column(String)
    city = Column(String)
    state = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="addresses")
