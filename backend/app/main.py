import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1 import (
    auth_router,
    chats_router,
    dev_agents_router,
    documents_router,
    settings_router,
)
from app.core.config import settings
from app.core.database import Base, engine
from app.core.error_handlers import register_error_handlers
from app.core.logging_config import setup_logging
from app.core.rate_limiter import limiter
from app.middleware.correlation_id import CorrelationIdMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event handler for FastAPI application startup and shutdown."""
    setup_logging(settings.LOG_LEVEL)
    logger.info(
        f"Starting Council of Minds Backend in '{settings.ENVIRONMENT}' mode (v{settings.VERSION})"
    )
    logger.info(f"CORS Allowed Origins: {settings.ALLOWED_ORIGINS}")

    # In development or test environments, ensure tables are created if not using migrations
    if settings.ENVIRONMENT in ["development", "testing", "test"]:
        logger.info("Verifying database schema...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    yield
    logger.info("Shutting down Council of Minds Backend.")
    await engine.dispose()


app = FastAPI(
    title="Council of Minds API",
    version=settings.VERSION,
    description="Backend API for Council of Minds monorepo",
    lifespan=lifespan,
)

# Register global rate limiter state and exception handlers
app.state.limiter = limiter
register_error_handlers(app)

# Register Middlewares (executed in LIFO order: CORS -> CorrelationID -> SlowAPI -> Route)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(documents_router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(chats_router, prefix="/api/v1/chats", tags=["Chats"])
app.include_router(settings_router, prefix="/api/v1/settings", tags=["Settings"])

if settings.ENVIRONMENT.lower() not in ["production", "prod"]:
    app.include_router(
        dev_agents_router, prefix="/api/v1/dev/agents", tags=["Dev / Internal"]
    )


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint returning status, environment, and version."""
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION,
    }
