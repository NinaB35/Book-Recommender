from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, Token, UserBase
from app.security import authenticate_user, create_access_token, get_password_hash

router = APIRouter(
    tags=["user"]
)


@router.post("/register")
async def register(
        user_data: Annotated[UserCreate, Body()],
        db: Annotated[AsyncSession, Depends(get_db)]
) -> UserBase:
    existing_email = await User.get_by_email(db, str(user_data.email))
    if existing_email is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    existing_username = await User.get_by_username(db, user_data.username)
    if existing_username is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=str(user_data.email),
        hashed_password=hashed_password
    )
    db.add(new_user)
    await db.commit()
    return UserBase.model_validate(new_user)


@router.post("/login")
async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Annotated[AsyncSession, Depends(get_db)]
) -> Token:
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.id})

    return Token(access_token=access_token, token_type="bearer")
