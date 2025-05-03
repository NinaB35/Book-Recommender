from typing import Annotated, List, Optional

from fastapi import Query
from pydantic import BaseModel, ConfigDict

from .author import AuthorGet
from .genre import GenreGet
from .rating import RatingGet


class BookBase(BaseModel):
    title: Annotated[
        str,
        Query(min_length=1, max_length=200, examples=["Гарри Поттер и философский камень"])
    ]
    publication_year: Annotated[
        int,
        Query(ge=1000, le=2100, examples=[1997])
    ]
    author_id: Annotated[
        int,
        Query(ge=1, examples=[1])
    ]
    genre_ids: Annotated[
        List[int],
        Query(min_items=1, examples=[[1, 2]])
    ]

    model_config = ConfigDict(from_attributes=True)


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[Annotated[
        str,
        Query(min_length=1, max_length=200, examples=["Гарри Поттер и философский камень"])
    ]] = None
    publication_year: Optional[Annotated[
        int,
        Query(ge=1000, le=2100, examples=[1997])
    ]] = None
    author_id: Optional[Annotated[
        int,
        Query(ge=1, examples=[1])
    ]] = None
    genre_ids: Optional[Annotated[
        List[int],
        Query(min_items=1, examples=[[1, 2]])
    ]] = None

    model_config = ConfigDict(from_attributes=True)


class BookGet(BaseModel):
    id: int
    title: Annotated[
        str,
        Query(min_length=1, max_length=200, examples=["Гарри Поттер и философский камень"])
    ]
    publication_year: Annotated[
        int,
        Query(ge=1000, le=2100, examples=[1997])
    ]
    author: AuthorGet
    genres: List[GenreGet]
    ratings: List[RatingGet]
    average_rating: float

    model_config = ConfigDict(from_attributes=True)


class BookGetQuery(BaseModel):
    skip: Annotated[int, Query(ge=0)] = 0
    limit: Annotated[int, Query(ge=1, le=1000)] = 100
    author_id: Optional[Annotated[int, Query(ge=1)]] = None
    genre_id: Optional[Annotated[int, Query(ge=1)]] = None
    year_from: Optional[Annotated[int, Query(ge=1000)]] = None
    year_to: Optional[Annotated[int, Query(le=2100)]] = None
