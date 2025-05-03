from typing import Annotated, Optional

from fastapi import Query
from pydantic import BaseModel, ConfigDict

from app.schemas import PrimaryKey


class RatingBase(BaseModel):
    rating: Annotated[
        int,
        Query(ge=1, le=10, description="Оценка от 1 до 10", examples=[9])
    ]
    review: Optional[Annotated[
        str,
        Query(max_length=1000, examples=["Отличная книга, рекомендую!"])
    ]] = None

    model_config = ConfigDict(from_attributes=True)


class RatingCreate(RatingBase):
    book_id: PrimaryKey


class RatingUpdate(BaseModel):
    rating: Optional[Annotated[
        int,
        Query(ge=1, le=10, description="Оценка от 1 до 10", examples=[4])
    ]] = None
    review: Optional[Annotated[
        str,
        Query(max_length=1000, examples=["Не очень хорошая книга"])
    ]] = None

    model_config = ConfigDict(from_attributes=True)


class RatingGet(RatingBase):
    id: int
    book_id: int
