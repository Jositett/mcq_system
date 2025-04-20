from sqlalchemy.orm import Session
from app.db import models
from app.schemas.user import UserCreate
from app.core import security
from sqlalchemy.exc import IntegrityError


def create_user(db: Session, user: UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role=user.role,
        is_active=True,
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        return None

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return None
    if not security.verify_password(password, user.hashed_password):
        return None
    return user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def list_users(db: Session):
    return db.query(models.User).all()

def update_user(db: Session, user_id: int, full_name: str = None, password: str = None):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None
    if full_name is not None:
        user.full_name = full_name
    if password is not None:
        user.hashed_password = security.get_password_hash(password)
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True
