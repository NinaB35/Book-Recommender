from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import jwt
import pytest
from fastapi import HTTPException, status

from app.environment import settings
from app.models import User
from app.security import (
    verify_password,
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_admin,
)


@pytest.mark.asyncio
async def test_verify_password_correct():
    plain_password = "password123"
    hashed_password = get_password_hash(plain_password)
    assert verify_password(plain_password, hashed_password) is True


@pytest.mark.asyncio
async def test_get_password_hash():
    password = "testpass"
    hashed = get_password_hash(password)
    assert hashed != password
    assert isinstance(hashed, str)


@pytest.mark.asyncio
async def test_authenticate_user_success(db_session):
    mock_user = User(
        id=1,
        email="test@example.com",
        hashed_password=get_password_hash("correct"),
        is_admin=False,
    )

    with patch.object(User, "get_by_email", AsyncMock(return_value=mock_user)):
        user = await authenticate_user(db_session, "test@example.com", "correct")
        assert user == mock_user


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(db_session):
    mock_user = User(
        id=1,
        email="test@example.com",
        hashed_password=get_password_hash("correct"),
        is_admin=False,
    )

    with patch.object(User, "get_by_email", AsyncMock(return_value=mock_user)):
        user = await authenticate_user(db_session, "test@example.com", "wrong")
        assert user is None


@pytest.mark.asyncio
async def test_authenticate_user_not_found(db_session):
    with patch.object(User, "get_by_email", AsyncMock(return_value=None)):
        user = await authenticate_user(db_session, "nonexistent@example.com", "pass")
        assert user is None


@pytest.mark.asyncio
async def test_create_access_token():
    test_data = {"sub": "1"}
    token = create_access_token(test_data)

    decoded = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )

    assert decoded["sub"] == "1"
    assert "exp" in decoded


@pytest.mark.asyncio
async def test_get_current_user_success(db_session):
    mock_user = User(id=1, email="test@example.com", hashed_password="hashed", is_admin=False)
    test_token = create_access_token({"sub": "1"})

    with patch.object(User, "get_by_id", AsyncMock(return_value=mock_user)):
        user = await get_current_user(db_session, test_token)
        assert user == mock_user


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(db_session):
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(db_session, "invalid_token")
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_current_user_expired_token(db_session):
    expired_token = jwt.encode(
        {
            "sub": "1",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1)
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(db_session, expired_token)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_current_user_not_found(db_session):
    test_token = create_access_token({"sub": 999})

    with patch.object(User, "get_by_id", AsyncMock(return_value=None)):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(db_session, test_token)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_current_admin_success():
    admin_user = User(id=1, email="admin@example.com", hashed_password="hashed", is_admin=True)
    assert await get_current_admin(admin_user) == admin_user


@pytest.mark.asyncio
async def test_get_current_admin_not_admin():
    regular_user = User(id=2, email="user@example.com", hashed_password="hashed", is_admin=False)

    with pytest.raises(HTTPException) as exc_info:
        await get_current_admin(regular_user)
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
