from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config import settings
from app.exceptions import AppException, app_exception_handler
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limit import limiter
from app.routers import auth, health, users


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
        yield

    app = FastAPI(
        title=settings.APP_NAME,
        description=(
            "Production-ready FastAPI boilerplate with JWT auth, RBAC, "
            "async SQLAlchemy, Celery workers, and full test coverage."
        ),
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── State ──────────────────────────────────────────────────────────────────
    app.state.limiter = limiter

    # ── Middleware ─────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(LoggingMiddleware)

    # ── Exception handlers ─────────────────────────────────────────────────────
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "NOT_FOUND",
                "message": "Route not found",
                "status_code": 404,
            },
        )

    # ── Routers ────────────────────────────────────────────────────────────────
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(users.router)

    return app


app = create_app()
