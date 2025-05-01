from fastapi import FastAPI

from app.routers import user

app = FastAPI(title="Book Recommender API", version="1.0.0")

app.include_router(user.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
