from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Genre(Base):
    __tablename__ = "genre"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)

    books: Mapped[list["Book"]] = relationship(
        secondary="book_genres",
        back_populates="genres"
    )
