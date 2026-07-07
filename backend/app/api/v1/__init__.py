from app.api.v1.auth import router as auth_router
from app.api.v1.chats import router as chats_router
from app.api.v1.dev_agents import router as dev_agents_router
from app.api.v1.documents import router as documents_router
from app.api.v1.settings import router as settings_router

__all__ = [
    "auth_router",
    "documents_router",
    "dev_agents_router",
    "chats_router",
    "settings_router",
]
