from typing import Optional

from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Rating(Base):
    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", onupdate="cascade", ondelete="cascade"))
    book_id: Mapped[int] = mapped_column(ForeignKey("book.id", onupdate="cascade", ondelete="cascade"))
    rating: Mapped[int] = mapped_column(Integer)
    review: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    user: Mapped["User"] = relationship(back_populates="ratings")
    book: Mapped["Book"] = relationship(back_populates="ratings")
