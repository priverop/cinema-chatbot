from fastapi import FastAPI

from app.api.routers.movies import router as movies_router
from app.api.routers.showtimes import router as showtimes_router
from app.api.routers.theaters import router as theaters_router

app = FastAPI()
app.include_router(theaters_router)
app.include_router(movies_router)
app.include_router(showtimes_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}
