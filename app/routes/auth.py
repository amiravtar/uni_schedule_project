from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing_extensions import Annotated

from app.core.security import create_access_token, verify_password
from app.crud.user import create_user, get_user_by_username
from app.db.session import get_session
from app.schemas.user import Token, UserCreate

SessionDep = Annotated[Session, Depends(get_session)]

router = APIRouter()


@router.post(
    "/register",
    response_model=dict,
    responses={
        400: {
            "description": "User already exiest",
            "content": {"application/json": {"example": {"detail": "Username already exists"}}},
        },
    },
)
def register(user: UserCreate, session: SessionDep):
    existing_user = get_user_by_username(session, user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )
    create_user(session, user.username, user.password)
    return {"message": "User registered successfully"}


@router.post("/login", response_model=Token)
def login(user: UserCreate, session: SessionDep):
    db_user = get_user_by_username(session, user.username)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
        )
    token = create_access_token({"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}
