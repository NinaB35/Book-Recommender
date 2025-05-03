from typing import Annotated, List, Optional

from fastapi import APIRouter, HTTPException, status, Query, Body
from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload

from app.database import AsyncDB
from app.models import Book, BookGenre, Author, Genre
from app.schemas import PrimaryKey
from app.schemas.book import BookGet, BookCreate, BookUpdate

router = APIRouter(
    prefix="/books",
    tags=["books"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_book(
        book_data: Annotated[BookCreate, Body()],
        db: AsyncDB
) -> BookGet:
    author = await Author.get_by_id(db, book_data.author_id)
    if author is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found"
        )
    genres = await db.execute(
        select(Genre).where(Genre.id.in_(book_data.genre_ids))
    )
    genres = genres.scalars().all()
    if len(genres) != len(book_data.genre_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more genres not found"
        )
    book = Book(
        title=book_data.title,
        publication_year=book_data.publication_year,
        author_id=book_data.author_id
    )
    db.add(book)
    await db.flush()

    for genre_id in book_data.genre_ids:
        db.add(BookGenre(book_id=book.id, genre_id=genre_id))

    book = await Book.get_by_id_full(db, book.id)
    book = BookGet.model_validate(book)
    await db.commit()
    return book


@router.get("/{book_id}")
async def get_book(
        book_id: PrimaryKey,
        db: AsyncDB
) -> BookGet:
    book = await Book.get_by_id_full(db, book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    book = BookGet.model_validate(book)
    return book


@router.get("/")
async def get_books(
        db: AsyncDB,
        skip: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(ge=1, le=1000)] = 100,
        author_id: Annotated[Optional[int], Query(ge=1)] = None,
        genre_id: Annotated[Optional[int], Query(ge=1)] = None,
        year_from: Annotated[Optional[int], Query(ge=1000)] = None,
        year_to: Annotated[Optional[int], Query(le=2100)] = None
) -> List[BookGet]:
    query = (
        select(Book)
        .options(
            selectinload(Book.author),
            selectinload(Book.genres),
            selectinload(Book.ratings)
        )
    )
    if author_id is not None:
        query = query.where(Book.author_id == author_id)
    if genre_id is not None:
        query = query.join(Book.genres).where(Genre.id == genre_id)
    if year_from is not None:
        query = query.where(Book.publication_year >= year_from)
    if year_to is not None:
        query = query.where(Book.publication_year <= year_to)
    books = await db.execute(
        query
        .offset(skip)
        .limit(limit)
    )
    books = books.scalars().all()
    books = [BookGet.model_validate(book) for book in books]
    return books


@router.put("/{book_id}")
async def update_book(
        book_id: PrimaryKey,
        book_data: Annotated[BookUpdate, Body()],
        db: AsyncDB
) -> BookGet:
    book = await Book.get_by_id(db, book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    update_data = book_data.model_dump(exclude_unset=True)
    if len(update_data) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data to update"
        )

    book_update_data = {}
    if "title" in update_data:
        book_update_data["title"] = update_data["title"]
    if "publication_year" in update_data:
        book_update_data["publication_year"] = update_data["publication_year"]
    if "author_id" in update_data:
        author = await Author.get_by_id(db, update_data["author_id"])
        if author is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Author not found"
            )
        book_update_data["author_id"] = update_data["author_id"]

    book = await db.execute(
        update(Book)
        .where(Book.id == book_id)
        .values(book_update_data)
        .returning(Book)
    )
    book.scalar_one()

    if "genre_ids" in update_data:
        genres = await db.execute(
            select(Genre).where(Genre.id.in_(update_data["genre_ids"]))
        )
        genres = genres.scalars().all()
        if len(genres) != len(book_data.genre_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more genres not found"
            )

        await db.execute(
            delete(BookGenre).where(BookGenre.book_id == book_id)
        )
        for genre_id in update_data["genre_ids"]:
            db.add(BookGenre(book_id=book_id, genre_id=genre_id))

    book = await Book.get_by_id_full(db, book_id)
    book = BookGet.model_validate(book)
    await db.commit()
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
        book_id: PrimaryKey,
        db: AsyncDB
):
    book = await Book.get_by_id(db, book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    await db.delete(book)
    await db.commit()
