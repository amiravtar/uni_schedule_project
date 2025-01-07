from sqlmodel import Session, select

from app.core.security import hash_password
from app.models.user import User


def create_user(session: Session, username: str, password: str) -> User:
    hashed_password = hash_password(password)
    new_user = User(username=username, hashed_password=hashed_password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

def get_user_by_username(session: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()
