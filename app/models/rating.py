from typing import Optional

from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Rating(Base):
    __tablename__ = "ratings"

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
