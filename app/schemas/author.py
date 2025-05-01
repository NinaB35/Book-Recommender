from typing import Annotated, Optional

from fastapi import Query
from pydantic import BaseModel, ConfigDict

example_bio = """Джоан Роулинг — британская писательница, сценаристка и кинопродюсер. Наиболее известна как автор серии романов о Гарри Поттере в жанре фэнтези.

Роулинг обучалась в Эксетерском университете и получила степень бакалавра по французскому языку и классической филологии. После окончания университета переехала в Лондон, где работала секретарём в «Международной амнистии».

Во время поездки на поезде из Манчестера в Лондон в 1990 году у неё появилась идея романа о Гарри Поттере. В 1997 году был опубликован первый роман в серии — «Гарри Поттер и философский камень». Впоследствии Роулинг написала 6 сиквелов и 3 дополнения к этой серии."""

name_pattern = "^[a-zA-Zа-яА-ЯёЁ -.]+$"


class AuthorBase(BaseModel):
    name: Annotated[
        str,
        Query(
            min_length=2,
            max_length=100,
            pattern=name_pattern,
            examples=["Джоан Кэтлин Роулинг"]
        )
    ]
    bio: Optional[Annotated[
        str,
        Query(max_length=1000, examples=[example_bio])
    ]] = None

    model_config = ConfigDict(from_attributes=True)


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(AuthorBase):
    name: Optional[Annotated[
        str,
        Query(
            min_length=2,
            max_length=100,
            pattern=name_pattern,
            examples=["Джоан Кэтлин Роулинг"]
        )
    ]] = None


class AuthorGet(AuthorBase):
    id: int
    books_count: int = 0
