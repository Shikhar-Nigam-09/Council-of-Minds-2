import urllib.parse

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


def get_engine_url(url: str) -> tuple[str, dict]:
    """Parse database URL and return SQLAlchemy compatible async URL and connect_args."""
    connect_args = {}

    # Handle postgres:// or postgresql:// schemes to use asyncpg
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and not url.startswith(
        "postgresql+asyncpg://"
    ):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # Handle sslmode in query parameters for asyncpg (Neon PostgreSQL requirement)
    if "postgresql+asyncpg" in url:
        parsed = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed.query)

        if "sslmode" in query_params or "ssl" in query_params:
            ssl_mode = query_params.get("sslmode", query_params.get("ssl", [""]))[0]
            if ssl_mode in ["require", "required", "true", "1"]:
                connect_args["ssl"] = "require"

            # Remove sslmode/ssl from query string as asyncpg connect() doesn't accept it in URL
            new_query_params = {
                k: v for k, v in query_params.items() if k not in ["sslmode", "ssl"]
            }
            new_query = urllib.parse.urlencode(new_query_params, doseq=True)
            url = urllib.parse.urlunparse(parsed._replace(query=new_query))

    return url, connect_args


db_url, connect_args = get_engine_url(settings.DATABASE_URL)

engine_kwargs = {
    "connect_args": connect_args,
    "echo": settings.LOG_LEVEL == "DEBUG",
    "future": True,
}
if not db_url.startswith("sqlite"):
    engine_kwargs["pool_size"] = settings.DB_POOL_SIZE
    engine_kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW

engine = create_async_engine(db_url, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db():
    """FastAPI dependency for database session management."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
