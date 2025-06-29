from fastapi import FastAPI

from app.routers import user, author, genre, book, rating

app = FastAPI(title="Book Recommender API", version="1.0.0")

app.include_router(user.router)
app.include_router(author.router)
app.include_router(genre.router)

app.include_router(book.router)

app.include_router(rating.router)
