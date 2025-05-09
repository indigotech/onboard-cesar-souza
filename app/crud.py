from sqlalchemy.orm import Session
from . import models, schemas

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(name=user.name, email=user.email,password=user.password, birthDate=user.birthDate)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return user.name