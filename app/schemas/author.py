from typing import Annotated, Optional

from fastapi import Query
from pydantic import BaseModel, ConfigDict

EXAMPLE_BIO = """Джоан Роулинг — британская писательница, сценаристка и кинопродюсер. Наиболее известна как автор серии романов о Гарри Поттере в жанре фэнтези.

Роулинг обучалась в Эксетерском университете и получила степень бакалавра по французскому языку и классической филологии. После окончания университета переехала в Лондон, где работала секретарём в «Международной амнистии».

Во время поездки на поезде из Манчестера в Лондон в 1990 году у неё появилась идея романа о Гарри Поттере. В 1997 году был опубликован первый роман в серии — «Гарри Поттер и философский камень». Впоследствии Роулинг написала 6 сиквелов и 3 дополнения к этой серии."""

NAME_PATTERN = "^[a-zA-Zа-яА-ЯёЁ -.]+$"

EXAMPLE_BIO2 = """Джордж Рэймонд Ричард Мартин — американский писатель-фантаст, сценарист, продюсер и редактор. В 1970–1980-е годы получил известность благодаря рассказам и повестям в жанре научной фантастики, литературы ужасов и фэнтези.

Славу ему принёс выходящий с 1996 года фэнтезийный цикл «Песнь Льда и Огня», позднее экранизированный компанией HBO в виде популярного телесериала «Игра престолов»."""


class AuthorBase(BaseModel):
    name: Annotated[
        str,
        Query(
            min_length=2,
            max_length=100,
            pattern=NAME_PATTERN,
            examples=["Джоан Кэтлин Роулинг"]
        )
    ]
    bio: Optional[Annotated[
        str,
        Query(max_length=1000, examples=[EXAMPLE_BIO])
    ]] = None

    model_config = ConfigDict(from_attributes=True)


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(BaseModel):
    name: Optional[Annotated[
        str,
        Query(
            min_length=2,
            max_length=100,
            pattern=NAME_PATTERN,
            examples=["Джордж Р. Р. Мартин"]
        )
    ]] = None
    bio: Optional[Annotated[
        str,
        Query(max_length=1000, examples=[EXAMPLE_BIO2])
    ]] = None

    model_config = ConfigDict(from_attributes=True)


class AuthorGet(AuthorBase):
    id: int
    books_count: int = 0
