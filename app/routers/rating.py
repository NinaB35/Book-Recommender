from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncDB
from app.models import Rating, Book, User
from app.schemas import PrimaryKey, Skip, Limit
from app.schemas.rating import RatingGet, RatingCreate, RatingUpdate
from app.security import get_current_user

router = APIRouter(
    prefix="/ratings",
    tags=["ratings"]
)


async def update_book_rating(db: AsyncSession, book_id: int):
    avg_rating = await db.execute(
        select(func.avg(Rating.rating))
        .where(Rating.book_id == book_id)
    )
    avg_rating = avg_rating.scalar() or 0.0
    await db.execute(
        update(Book)
        .where(Book.id == book_id)
        .values(average_rating=round(avg_rating, 2))
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_rating(
        rating_data: Annotated[RatingCreate, Body()],
        db: AsyncDB,
        current_user: Annotated[User, Depends(get_current_user)]
) -> RatingGet:
    book = await Book.get_by_id(db, rating_data.book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    existing_rating = await Rating.get_by_user_and_book(db, current_user.id, rating_data.book_id)
    if existing_rating is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already rated this book"
        )
    rating = Rating(
        user_id=current_user.id,
        book_id=rating_data.book_id,
        rating=rating_data.rating,
        review=rating_data.review
    )
    db.add(rating)
    await db.flush()
    await db.refresh(rating)
    await update_book_rating(db, rating.book_id)
    rating = RatingGet.model_validate(rating)
    await db.commit()
    return rating


@router.get("/{rating_id}")
async def get_rating(
        rating_id: PrimaryKey,
        db: AsyncDB
) -> RatingGet:
    rating = await Rating.get_by_id(db, rating_id)
    if rating is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )
    return RatingGet.model_validate(rating)


@router.get("/")
async def get_user_ratings(
        db: AsyncDB,
        current_user: Annotated[User, Depends(get_current_user)],
        skip: Skip = 0,
        limit: Limit = 100
) -> list[RatingGet]:
    ratings = await db.execute(
        select(Rating)
        .where(Rating.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    ratings = ratings.scalars().all()
    return [RatingGet.model_validate(r) for r in ratings]


@router.put("/{rating_id}")
async def update_rating(
        rating_id: PrimaryKey,
        rating_data: Annotated[RatingUpdate, Body()],
        db: AsyncDB,
        current_user: Annotated[User, Depends(get_current_user)]
) -> RatingGet:
    rating = await Rating.get_by_id(db, rating_id)
    if rating is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )
    if rating.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own ratings"
        )

    update_data = rating_data.model_dump(exclude_unset=True)
    if len(update_data) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data to update"
        )

    rating = await db.execute(
        update(Rating)
        .where(Rating.id == rating_id)
        .values(update_data)
        .returning(Rating)
    )
    rating = rating.scalar_one()
    rating = RatingGet.model_validate(rating)
    await update_book_rating(db, rating.book_id)
    await db.commit()
    return rating


@router.delete("/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rating(
        rating_id: PrimaryKey,
        db: AsyncDB,
        current_user: Annotated[User, Depends(get_current_user)]
):
    rating = await Rating.get_by_id(db, rating_id)
    if rating is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )
    if rating.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own ratings"
        )
    await db.delete(rating)
    await update_book_rating(db, rating.book_id)
    await db.commit()
