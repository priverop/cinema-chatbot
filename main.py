from fastapi import FastAPI

from app.api.routers.theaters import router as theaters_router

app = FastAPI()
app.include_router(theaters_router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
