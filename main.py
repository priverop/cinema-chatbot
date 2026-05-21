from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routers.chat import router as chat_router
from app.api.routers.movies import router as movies_router
from app.api.routers.showtimes import router as showtimes_router
from app.api.routers.theaters import router as theaters_router
from app.domain.errors import (
    LLMError,
    LLMInvalidRequest,
    LLMRateLimited,
    LLMUnavailable,
)

app = FastAPI()
app.include_router(theaters_router)
app.include_router(movies_router)
app.include_router(showtimes_router)
app.include_router(chat_router)


@app.exception_handler(LLMUnavailable)
def handle_llm_unavailable(_: Request, exc: LLMUnavailable) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"detail": "LLM service unavailable. Try again later."},
    )


@app.exception_handler(LLMRateLimited)
def handle_llm_rate_limited(_: Request, exc: LLMRateLimited) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": "LLM rate limit reached. Slow down."},
    )


@app.exception_handler(LLMInvalidRequest)
def handle_llm_invalid_request(_: Request, exc: LLMInvalidRequest) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": f"Invalid LLM request: {exc}"},
    )


@app.exception_handler(LLMError)
def handle_llm_error(_: Request, exc: LLMError) -> JSONResponse:
    return JSONResponse(
        status_code=502,
        content={"detail": "Upstream LLM failure."},
    )

@app.get("/")
def read_root():
    return {"Hello": "World"}
