from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.orm import DeclarativeBase


class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс моделей."""

    @classmethod
    async def get_by_id(cls, db: AsyncSession, obj_id: int) -> Optional["Base"]:
        """
        Получение объекта по id.

        :param db: Сессия базы данных.
        :param obj_id: Идентификатор объекта.
        :return: Объект.
        """
        result = await db.execute(select(cls).where(cls.id == obj_id))
        return result.scalar_one_or_none()
