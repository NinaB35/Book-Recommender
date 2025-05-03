from typing import Optional

from sqlalchemy import Integer, String, Float, ForeignKey, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from .base import Base


class Book(Base):
    """Модель книги."""

    __tablename__ = "book"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment="Идентификатор книги"
    )
    title: Mapped[str] = mapped_column(
        String(100),
        comment="Название книги"
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey("author.id", onupdate="cascade", ondelete="cascade"),
        index=True,
        comment="Идентификатор автора"
    )
    publication_year: Mapped[int] = mapped_column(
        Integer,
        comment="Год издания"
    )
    average_rating: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        comment="Средний рейтинг книги"
    )

    author: Mapped["Author"] = relationship(back_populates="books")
    genres: Mapped[list["Genre"]] = relationship(
        secondary="book_genre",
        back_populates="books"
    )
    ratings: Mapped[list["Rating"]] = relationship(back_populates="book")

    @classmethod
    async def get_by_id_full(cls, db: AsyncSession, book_id: int) -> Optional["Book"]:
        """
        Полное получение книги с автором, жанрами и рейтингами.

        :param db: Сессия базы данных.
        :param book_id: Идентификатор книги.
        :return: Объект книги.
        """
        result = await db.execute(
            select(cls)
            .options(
                selectinload(cls.author),
                selectinload(cls.genres),
                selectinload(cls.ratings)
            )
            .where(cls.id == book_id))
        return result.scalar_one_or_none()
