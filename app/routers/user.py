from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm

from app.database import AsyncDB
from app.models.user import User
from app.schemas.user import UserCreate, Token, UserGet
from app.security import authenticate_user, create_access_token, get_password_hash, CurrentUser

router = APIRouter(
    tags=["user"]
)


@router.post("/register")
async def register(
        user_data: Annotated[UserCreate, Body()],
        db: AsyncDB
) -> UserGet:
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
    user = User(
        username=user_data.username,
        email=str(user_data.email),
        hashed_password=hashed_password
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    user = UserGet.model_validate(user)
    await db.commit()
    return user


@router.post("/login")
async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: AsyncDB
) -> Token:
    user = await authenticate_user(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({"sub": str(user.id)})
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me")
async def users_me(
        current_user: CurrentUser,
) -> UserGet:
    return UserGet.model_validate(current_user)
