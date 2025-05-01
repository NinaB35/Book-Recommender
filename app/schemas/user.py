from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    username: Annotated[str, Query(min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")]

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    password: Annotated[str, Query(min_length=8, max_length=50)]


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
