from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from collections.abc import Sequence
from collections.abc import AsyncIterator

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.routes import api_router, auth_router
from backend.ml.predictor import case_predictor
from backend.services.errors import ExtractionError
from backend.services.database import initialize_database

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


def configured_origins() -> Sequence[str]:
    origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if origin.strip()]
    if not origins or "*" in origins:
        raise RuntimeError("CORS_ORIGINS must contain one or more explicit frontend origins; wildcard origins are not allowed.")
    return origins


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    initialize_database()
    case_predictor.load()
    yield


app = FastAPI(
    title="NyayaSetu API",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(configured_origins()),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=600,
)
app.include_router(api_router)
app.include_router(auth_router)


@app.get("/", include_in_schema=False)
def api_root() -> dict[str, str]:
    return {"service": "NyayaSetu API", "status": "ok"}


@app.exception_handler(HTTPException)
async def handle_http_error(_request: Request, exception: HTTPException) -> JSONResponse:
    detail = exception.detail
    if isinstance(detail, dict) and "code" in detail and "message" in detail:
        error_detail = detail
    else:
        error_detail = {"code": f"http_{exception.status_code}", "message": str(detail)}
    return JSONResponse(
        status_code=exception.status_code,
        content={"detail": error_detail},
        headers=exception.headers,
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_error(_request: Request, _exception: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"detail": {"code": "validation_error", "message": "The request payload failed validation."}},
    )


@app.exception_handler(ExtractionError)
async def handle_extraction_error(_request: Request, exception: ExtractionError) -> JSONResponse:
    return JSONResponse(
        status_code=exception.status_code,
        content={"detail": {"code": exception.code, "message": exception.message}},
    )
