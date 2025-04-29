from fastapi import FastAPI

app = FastAPI(title="Book Recommender API", version="1.0.0")


@app.get("/")
async def root():
    return {"message": "Hello World"}
