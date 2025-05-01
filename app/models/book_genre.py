from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class BookGenre(Base):
    __tablename__ = "book_genre"

    book_id: Mapped[int] = mapped_column(
        ForeignKey("book.id", onupdate="cascade", ondelete="cascade"),
        primary_key=True
    )
    genre_id: Mapped[int] = mapped_column(
        ForeignKey("genre.id", onupdate="cascade", ondelete="cascade"),
        primary_key=True
    )
