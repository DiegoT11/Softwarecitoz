import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.config import get_settings
from src.exceptions import (
    DomainError,
    ExternalServiceError,
    ForbiddenError,
    NotFoundError,
    RateLimitedError,
)
from src.profiles.router import router as profiles_router
from src.steam.client import SteamClient

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Crea un solo cliente HTTP hacia Steam para toda la app."""
    async with httpx.AsyncClient(
        base_url=settings.steam_api_base_url,
        timeout=httpx.Timeout(settings.steam_timeout_seconds),
        limits=httpx.Limits(
            max_connections=20, max_keepalive_connections=10),
    ) as http:
        app.state.steam_client = SteamClient(http, settings.steam_api_key)
        yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
    debug=settings.app_env == "dev",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(profiles_router)


_STATUS_MAP = {
    NotFoundError: 404,
    ForbiddenError: 403,
    RateLimitedError: 503,
    ExternalServiceError: 502,
}


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    status_code = next(
        (code for cls, code in _STATUS_MAP.items() if isinstance(exc, cls)),
        500,
    )
    logger.warning(
        "domain_error",
        extra={"error_code": exc.error_code, "path": request.url.path},
    )
    return JSONResponse(
        status_code=status_code,
        content={"detail": str(exc), "error_code": exc.error_code},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
        request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Datos inválidos",
            "error_code": "validation_error",
            "errors": jsonable_encoder(exc.errors()),
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
        request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_code": "http_error"},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("unhandled_exception", extra={"path": request.url.path})
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "error_code": "internal_error",
        },
    )


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
