from sqlalchemy.orm import Session
from .models import User

def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, username: str, email: str, hashed_password: str, token: str):
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        verification_token=token,
        is_active=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_user(db: Session, token: str):
    user = db.query(User).filter(User.verification_token == token).first()
    if user:
        user.is_active = True
        user.verification_token = None
        db.commit()
    return user
