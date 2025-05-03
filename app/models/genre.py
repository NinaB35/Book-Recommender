from typing import Optional

from sqlalchemy import Integer, String, Index, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Genre(Base):
    """Модель жанра."""

    __tablename__ = "genre"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment="Идентификатор жанра"
    )
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        comment="Название жанра"
    )

    books: Mapped[list["Book"]] = relationship(
        secondary="book_genre",
        back_populates="genres"
    )

    __table_args__ = (
        Index(
            'ix_genre_lower_name',
            func.lower(name),
            unique=True
        ),
    )

    @classmethod
    async def get_by_name(cls, db: AsyncSession, name: str) -> Optional["Genre"]:
        """
        Получение жанра по названию.

        :param db: Сессия базы данных.
        :param name: Название жанра.
        :return: Объект жанра.
        """
        result = await db.execute(select(cls).where(func.lower(cls.name) == func.lower(name)))
        return result.scalar_one_or_none()
