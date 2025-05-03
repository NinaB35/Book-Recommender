from sqlalchemy import Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment="Идентификатор пользователя"
    )
    username: Mapped[str] = mapped_column(
        String,
        unique=True,
        comment="Уникальный юзернейм пользователя"
    )
    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        comment="Уникальная электронная почта пользователя"
    )
    hashed_password: Mapped[str] = mapped_column(
        String,
        comment="Хэш пароля пользователя"
    )

    ratings: Mapped[list["Rating"]] = relationship(back_populates="user")

    @classmethod
    async def get_by_username(cls, db: AsyncSession, username: str):
        result = await db.execute(select(cls).where(cls.username == username))
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_email(cls, db: AsyncSession, email: str):
        result = await db.execute(select(cls).where(cls.email == email))
        return result.scalar_one_or_none()
