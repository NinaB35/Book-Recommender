from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, ConfigDict


class GenreBase(BaseModel):
    name: Annotated[
        str,
        Query(
            min_length=3,
            max_length=100,
            pattern="^[a-zA-Zа-яА-ЯёЁ -]+$",
            examples=["Исторический роман", "Научная фантастика"]
        )
    ]

    model_config = ConfigDict(from_attributes=True)


class GenreCreate(GenreBase):
    pass


class GenreUpdate(GenreBase):
    pass


class GenreGet(GenreBase):
    id: int
