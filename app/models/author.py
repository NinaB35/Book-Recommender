from typing import Optional

from sqlalchemy import Integer, String, func, Index
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Author(Base):
    """Модель автора книги."""

    __tablename__ = "author"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment="Идентификатор автора"
    )
    name: Mapped[str] = mapped_column(
        String(100),
        comment="Полное имя автора"
    )
    bio: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
        comment="Биография автора"
    )

    books: Mapped[list["Book"]] = relationship(
        back_populates="author"
    )

    __table_args__ = (
        Index(
            'ix_author_lower_name',
            func.lower(name),
            unique=True
        ),
    )

    @classmethod
    async def get_by_name(cls, db: AsyncSession, name: str) -> Optional["Author"]:
        """
        Получение автора по имени.

        :param db: Сессия базы данных.
        :param name: Имя автора.
        :return: Объект автора.
        """
        result = await db.execute(select(cls).where(func.lower(cls.name) == func.lower(name)))
        return result.scalar_one_or_none()
