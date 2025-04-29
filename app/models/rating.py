from typing import Optional

from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base
from models.book import Book
from models.user import User


class Rating(Base):
    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), onupdate="cascade", ondelete="cascade")
    book_id: Mapped[int] = mapped_column(ForeignKey(Book.id), onupdate="cascade", ondelete="cascade")
    rating: Mapped[int] = mapped_column(Integer)
    review: Optional[Mapped[str]] = mapped_column(String, nullable=True)
