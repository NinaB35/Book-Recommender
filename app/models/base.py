from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.orm import DeclarativeBase


class Base(AsyncAttrs, DeclarativeBase):
    pass

    @classmethod
    async def get_by_id(cls, db: AsyncSession, obj_id: int):
        result = await db.execute(select(cls).where(cls.id == obj_id))
        return result.scalar_one_or_none()
