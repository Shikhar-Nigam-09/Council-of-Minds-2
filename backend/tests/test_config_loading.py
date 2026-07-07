from app.core.config import Settings, settings


def test_settings_load_from_env_file():
    """Verify that all required settings load cleanly from .env and match expected types."""
    s = Settings()

    # Application
    assert isinstance(s.ENVIRONMENT, str)
    assert isinstance(s.APP_PORT, int)
    assert isinstance(s.ALLOWED_ORIGINS, list)
    assert isinstance(s.LOG_LEVEL, str)
    assert isinstance(s.VERSION, str)

    # Database
    assert isinstance(s.DATABASE_URL, str)
    assert s.DATABASE_URL.startswith(("sqlite+aiosqlite://", "postgresql+asyncpg://"))

    # JWT & Authentication
    assert isinstance(s.JWT_SECRET_KEY, str)
    assert isinstance(s.JWT_ALGORITHM, str)
    assert isinstance(s.ACCESS_TOKEN_EXPIRE_MINUTES, int)
    assert isinstance(s.REFRESH_TOKEN_EXPIRE_DAYS, int)

    # Cloudinary & Documents
    assert isinstance(s.CLOUDINARY_CLOUD_NAME, str)
    assert isinstance(s.CLOUDINARY_API_KEY, str)
    assert isinstance(s.CLOUDINARY_API_SECRET, str)
    assert isinstance(s.MAX_UPLOAD_SIZE_MB, int)
    assert isinstance(s.ALLOWED_DOCUMENT_TYPES, list)

    # RAG & Embeddings
    assert isinstance(s.CHUNK_SIZE, int)
    assert isinstance(s.CHUNK_OVERLAP, int)
    assert isinstance(s.EMBEDDING_MODEL_NAME, str)

    # FAISS Lifecycle
    assert isinstance(s.FAISS_INDEX_CLOUDINARY_FOLDER, str)
    assert isinstance(s.INGESTION_STUCK_THRESHOLD_MINUTES, int)

    # Groq & Reasoning Agents
    assert isinstance(s.GROQ_API_KEY, str)
    assert isinstance(s.REASONING_MODEL_NAME, str)
    assert isinstance(s.AGENT_TIMEOUT_SECONDS, int)

    # Aggregator
    assert isinstance(s.AGGREGATOR_MODEL_NAME, str)
    assert isinstance(s.DEFAULT_AGENT_WEIGHTS, dict)
    assert "logical" in s.DEFAULT_AGENT_WEIGHTS

    # Confidence Engine
    assert isinstance(s.CONFIDENCE_WEIGHT_RETRIEVAL, float)
    assert isinstance(s.CONFIDENCE_WEIGHT_EVIDENCE, float)
    assert isinstance(s.CONFIDENCE_WEIGHT_AGREEMENT, float)

    # Chat & Conversation History
    assert isinstance(s.MAX_CHAT_HISTORY_MESSAGES, int)

    # Rate Limiting
    assert isinstance(s.RATE_LIMIT_AUTH_PER_MINUTE, str)
    assert isinstance(s.RATE_LIMIT_QUESTIONS_PER_MINUTE, str)

    # Database Pool & Performance
    assert isinstance(s.DB_POOL_SIZE, int)
    assert isinstance(s.DB_MAX_OVERFLOW, int)


def test_global_settings_singleton():
    """Verify that the exported settings singleton is instantiated properly."""
    assert settings is not None
    assert settings.APP_PORT == 8000
