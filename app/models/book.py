from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    author: Mapped[str] = mapped_column(String)
    genre: Mapped[str] = mapped_column(String)
    publication_year: Mapped[int] = mapped_column(Integer)
    average_rating: Mapped[float] = mapped_column(Float, default=0.0)
