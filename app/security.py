from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncDB
from app.environment import settings
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверка пароля.
    :param plain_password: Проверяемый пароль.
    :param hashed_password: Хешированный пароль.
    :return: True, если пароли совпадают.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Хеширование пароля.
    :param password: Пароль.
    :return: Хешированный пароль.
    """
    return pwd_context.hash(password)


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    """
    Аутентификация пользователя.
    :param db: Сессия базы данных.
    :param email: Почта пользователя.
    :param password: Введенный пароль пользователя.
    """
    user = await User.get_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict) -> str:
    """
    Генерация токена.
    :param data: Данные для токена.
    :return: JWT.
    """
    to_encode = data.copy()
    to_encode.update({
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_user(
        db: AsyncDB,
        token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    """
    Получение текущего пользователя по токену.
    :param db: Сессия базы данных.
    :param token: JWT.
    :return: Текущий пользователь.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user_id = int(user_id)
    except InvalidTokenError as exc:
        raise credentials_exception from exc
    user = await User.get_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
