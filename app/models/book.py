from sqlalchemy import Integer, String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Book(Base):
    __tablename__ = "book"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    author_id: Mapped[int] = mapped_column(ForeignKey("author.id", onupdate="cascade", ondelete="cascade"))
    publication_year: Mapped[int] = mapped_column(Integer)
    average_rating: Mapped[float] = mapped_column(Float, default=0.0)

    author: Mapped["Author"] = relationship(back_populates="books")
    genres: Mapped[list["Genre"]] = relationship(
        secondary="book_genre",
        back_populates="books"
    )
    ratings: Mapped[list["Rating"]] = relationship(back_populates="book")
