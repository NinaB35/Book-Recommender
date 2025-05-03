from typing import Optional

from sqlalchemy import Integer, ForeignKey, String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Rating(Base):
    __tablename__ = "rating"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment="Идентификатор рейтинга"
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", onupdate="cascade", ondelete="cascade"),
        index=True,
        comment="Идентификатор пользователя"
    )
    book_id: Mapped[int] = mapped_column(
        ForeignKey("book.id", onupdate="cascade", ondelete="cascade"),
        index=True,
        comment="Идентификатор книги"
    )
    rating: Mapped[int] = mapped_column(
        Integer,
        comment="Рейтинг книги"
    )
    review: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
        comment="Отзыв о книге"
    )

    user: Mapped["User"] = relationship(back_populates="ratings")
    book: Mapped["Book"] = relationship(back_populates="ratings")

    @classmethod
    async def get_by_user_and_book(cls, db, user_id: int, book_id: int):
        result = await db.execute(
            select(cls)
            .where(cls.user_id == user_id)
            .where(cls.book_id == book_id)
        )
        return result.scalar_one_or_none()
