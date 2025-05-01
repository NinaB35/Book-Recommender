from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.environment import settings

engine = create_async_engine(settings.DB_URL, echo=True)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        yield session


AsyncDB = Annotated[AsyncSession, Depends(get_db)]
