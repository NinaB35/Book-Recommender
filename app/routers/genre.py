from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Body
from sqlalchemy import select, update

from app.database import AsyncDB
from app.models.genre import Genre
from app.schemas import PrimaryKey, Skip, Limit
from app.schemas.genre import GenreGet, GenreCreate, GenreUpdate

router = APIRouter(
    prefix="/genres",
    tags=["genres"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_genre(
        genre_data: Annotated[GenreCreate, Body()],
        db: AsyncDB
) -> GenreGet:
    existing_genre = await Genre.get_by_name(db, genre_data.name)
    if existing_genre:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Genre with this name already exists"
        )

    new_genre = Genre(name=genre_data.name)
    db.add(new_genre)
    await db.commit()
    await db.refresh(new_genre)
    return GenreGet.model_validate(new_genre)


@router.get("/{genre_id}")
async def get_genre(
        genre_id: PrimaryKey,
        db: AsyncDB
) -> GenreGet:
    genre = await Genre.get_by_id(db, genre_id)
    if genre is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Genre not found"
        )
    return genre


@router.get("/")
async def get_genres(
        db: AsyncDB,
        skip: Skip = 0,
        limit: Limit = 100
) -> list[GenreGet]:
    result = await db.execute(
        select(Genre)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.put("/{genre_id}")
async def update_genre(
        genre_id: PrimaryKey,
        genre_data: Annotated[GenreUpdate, Body()],
        db: AsyncDB
) -> GenreGet:
    genre = await Genre.get_by_id(db, genre_id)
    if not genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Genre not found"
        )

    update_data = genre_data.model_dump(exclude_unset=True)

    existing_genre = await Genre.get_by_name(db, update_data["name"])
    if existing_genre is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Genre with this name already exists"
        )

    genre = await db.execute(
        update(Genre)
        .where(Genre.id == genre_id)
        .values(update_data)
        .returning(Genre)
    )
    genre = genre.scalar_one()
    await db.commit()
    return GenreGet.model_validate(genre)


@router.delete("/{genre_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_genre(
        genre_id: PrimaryKey,
        db: AsyncDB
):
    genre = await Genre.get_by_id(db, genre_id)
    if not genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Genre not found"
        )

    await db.delete(genre)
    await db.commit()
