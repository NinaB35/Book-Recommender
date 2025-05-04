from typing import Annotated

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import AsyncDB
from app.environment import settings
from app.models import Rating, Book
from app.models.user import User
from app.schemas import Limit
from app.schemas.book import BookGet
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


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Косинусное сходство между двумя векторами."""
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    return dot_product / (norm_a * norm_b) if norm_a > 0 and norm_b > 0 else 0


async def get_fallback_recommendations(db: AsyncDB, limit: int) -> list[BookGet]:
    """Рекомендации без учета схожести пользователей."""
    books = await db.execute(
        select(Book)
        .options(
            selectinload(Book.author),
            selectinload(Book.genres),
            selectinload(Book.ratings)
        )
        .order_by(Book.average_rating.desc())
        .limit(limit)
    )
    books = books.scalars().all()
    return [BookGet.model_validate(book) for book in books]


@router.get("/recommendations")
async def recommendations(
        current_user: CurrentUser,
        db: AsyncDB,
        limit: Limit = 100
) -> list[BookGet]:
    ratings = await db.execute(
        select(
            Rating.user_id,
            Rating.book_id,
            Rating.rating
        )
    )
    ratings = ratings.all()
    if len(ratings) == 0:
        return []

    user_ids = await db.execute(select(User.id))
    user_ids = user_ids.scalars().all()
    book_ids = await db.execute(select(Book.id))
    book_ids = book_ids.scalars().all()

    user_to_idx = {user_id: i for i, user_id in enumerate(user_ids)}
    book_to_idx = {book_id: i for i, book_id in enumerate(book_ids)}
    current_user_idx = user_to_idx[current_user.id]

    rating_matrix = np.zeros((len(user_ids), len(book_ids)))
    for user_id, book_id, rating in ratings:
        rating_matrix[user_to_idx[user_id], book_to_idx[book_id]] = rating

    user_means = np.where(
        rating_matrix.sum(axis=1) > 0,
        rating_matrix.sum(axis=1) / (rating_matrix != 0).sum(axis=1),
        0
    )
    rating_matrix_norm = rating_matrix - user_means[:, np.newaxis]

    similarities = np.zeros(len(user_ids))
    for i in range(len(user_ids)):
        if i != current_user_idx:
            similarities[i] = cosine_similarity(
                rating_matrix_norm[current_user_idx],
                rating_matrix_norm[i]
            )

    top_n = min(settings.TOP_N_USERS, len(user_ids) - 1)
    top_user_indices = np.argsort(similarities)[-top_n:][::-1]

    if len(top_user_indices) == 0:
        return await get_fallback_recommendations(db, limit)

    recommended_books = np.zeros(len(book_ids))
    current_user_no_ratings = rating_matrix[current_user_idx] == 0

    for user_idx in top_user_indices:
        if similarities[user_idx] > 0:
            user_ratings = rating_matrix[user_idx]
            mask = current_user_no_ratings & (user_ratings > 0)
            recommended_books[mask] += user_ratings[mask] * similarities[user_idx]

    top_book_indices = np.argsort(recommended_books)[-limit:][::-1]
    recommended_book_ids = [book_ids[i] for i in top_book_indices if recommended_books[i] > 0]

    if len(recommended_book_ids) == 0:
        return await get_fallback_recommendations(db, limit)

    books = await db.execute(
        select(Book)
        .options(
            selectinload(Book.author),
            selectinload(Book.genres),
            selectinload(Book.ratings)
        )
        .where(Book.id.in_(recommended_book_ids))
    )
    books = books.scalars().all()
    return [BookGet.model_validate(book) for book in books]
