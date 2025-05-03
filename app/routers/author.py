from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Body
from sqlalchemy import select, func, update

from app.database import AsyncDB
from app.models import Author, Book
from app.schemas import PrimaryKey, Skip, Limit
from app.schemas.author import AuthorGet, AuthorCreate, AuthorUpdate

router = APIRouter(
    prefix="/authors",
    tags=["authors"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_author(
        author_data: Annotated[AuthorCreate, Body()],
        db: AsyncDB
) -> AuthorGet:
    existing_author = await Author.get_by_name(db, author_data.name)
    if existing_author is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Author with this name already exists"
        )
    author = Author(name=author_data.name, bio=author_data.bio)
    db.add(author)
    await db.flush()
    await db.refresh(author)
    author = AuthorGet.model_validate(author)
    await db.commit()
    return author


@router.get("/{author_id}")
async def get_author(
        author_id: PrimaryKey,
        db: AsyncDB
) -> AuthorGet:
    author = await db.execute(
        select(
            Author,
            func.count(Book.id).label("books_count")
        )
        .outerjoin(Book, Author.id == Book.author_id)
        .where(Author.id == author_id)
        .group_by(Author.id)
    )
    author = author.scalar_one_or_none()
    if author is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found"
        )
    author = AuthorGet.model_validate(author)
    return author


@router.get("/")
async def get_authors(
        db: AsyncDB,
        skip: Skip = 0,
        limit: Limit = 100
) -> list[AuthorGet]:
    authors = await db.execute(
        select(
            Author,
            func.count(Book.id).label("books_count")
        )
        .outerjoin(Book, Author.id == Book.author_id)
        .group_by(Author.id)
        .offset(skip)
        .limit(limit)
    )
    authors = authors.scalars().all()
    authors = [AuthorGet.model_validate(author) for author in authors]
    return authors


@router.put("/{author_id}")
async def update_author(
        author_id: PrimaryKey,
        author_data: Annotated[AuthorUpdate, Body()],
        db: AsyncDB
) -> AuthorGet:
    author = await Author.get_by_id(db, author_id)
    if author is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found"
        )

    update_data = author_data.model_dump(exclude_unset=True)
    if len(update_data) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data to update"
        )

    if "name" in update_data:
        existing_author = await Author.get_by_name(db, author_data.name)
        if existing_author is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Author with this name already exists"
            )

    author = await db.execute(
        update(Author)
        .where(Author.id == author_id)
        .values(update_data)
        .returning(Author)
    )
    author = author.scalar_one()
    author = AuthorGet.model_validate(author)
    await db.commit()
    return author


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(
        author_id: PrimaryKey,
        db: AsyncDB
):
    author = await Author.get_by_id(db, author_id)
    if author is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found"
        )

    await db.delete(author)
    await db.commit()
