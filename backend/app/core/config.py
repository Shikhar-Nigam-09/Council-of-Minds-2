from typing import Dict, List, Union

from pydantic import AliasChoices, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized app settings loaded from env vars or .env file."""

    ENVIRONMENT: str = Field(
        default="development",
        validation_alias=AliasChoices("ENVIRONMENT", "BACKEND_ENVIRONMENT"),
    )
    APP_PORT: int = Field(
        default=8000,
        validation_alias=AliasChoices("APP_PORT", "BACKEND_APP_PORT"),
    )
    ALLOWED_ORIGINS: Union[str, List[str]] = Field(
        default=[
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
        ],
        validation_alias=AliasChoices("ALLOWED_ORIGINS", "BACKEND_ALLOWED_ORIGINS"),
    )
    LOG_LEVEL: str = Field(
        default="INFO",
        validation_alias=AliasChoices("LOG_LEVEL", "BACKEND_LOG_LEVEL"),
    )
    VERSION: str = Field(
        default="0.1.0",
        validation_alias=AliasChoices("VERSION", "BACKEND_VERSION"),
    )

    # Database Settings
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./council.db",
        validation_alias=AliasChoices("DATABASE_URL", "BACKEND_DATABASE_URL"),
    )
    DB_POOL_SIZE: int = Field(
        default=5,
        validation_alias=AliasChoices("DB_POOL_SIZE", "BACKEND_DB_POOL_SIZE"),
    )
    DB_MAX_OVERFLOW: int = Field(
        default=10,
        validation_alias=AliasChoices("DB_MAX_OVERFLOW", "BACKEND_DB_MAX_OVERFLOW"),
    )

    # JWT & Authentication Settings
    JWT_SECRET_KEY: str = Field(
        default="super-secret-jwt-key-for-development-only-change-in-prod",
        validation_alias=AliasChoices("JWT_SECRET_KEY", "BACKEND_JWT_SECRET_KEY"),
    )
    JWT_ALGORITHM: str = Field(
        default="HS256",
        validation_alias=AliasChoices("JWT_ALGORITHM", "BACKEND_JWT_ALGORITHM"),
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        validation_alias=AliasChoices(
            "ACCESS_TOKEN_EXPIRE_MINUTES", "BACKEND_ACCESS_TOKEN_EXPIRE_MINUTES"
        ),
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        validation_alias=AliasChoices(
            "REFRESH_TOKEN_EXPIRE_DAYS", "BACKEND_REFRESH_TOKEN_EXPIRE_DAYS"
        ),
    )

    # Cloudinary & Document Storage Settings
    CLOUDINARY_CLOUD_NAME: str = Field(
        default="your_cloud_name",
        validation_alias=AliasChoices(
            "CLOUDINARY_CLOUD_NAME", "BACKEND_CLOUDINARY_CLOUD_NAME"
        ),
    )
    CLOUDINARY_API_KEY: str = Field(
        default="your_api_key",
        validation_alias=AliasChoices(
            "CLOUDINARY_API_KEY", "BACKEND_CLOUDINARY_API_KEY"
        ),
    )
    CLOUDINARY_API_SECRET: str = Field(
        default="your_api_secret",
        validation_alias=AliasChoices(
            "CLOUDINARY_API_SECRET", "BACKEND_CLOUDINARY_API_SECRET"
        ),
    )
    MAX_UPLOAD_SIZE_MB: int = Field(
        default=10,
        validation_alias=AliasChoices(
            "MAX_UPLOAD_SIZE_MB", "BACKEND_MAX_UPLOAD_SIZE_MB"
        ),
    )
    ALLOWED_DOCUMENT_TYPES: Union[str, List[str]] = Field(
        default=["application/pdf", "text/plain", "text/markdown"],
        validation_alias=AliasChoices(
            "ALLOWED_DOCUMENT_TYPES", "BACKEND_ALLOWED_DOCUMENT_TYPES"
        ),
    )

    # RAG Ingestion & FAISS Vector Store Settings
    CHUNK_SIZE: int = Field(
        default=1000,
        validation_alias=AliasChoices("CHUNK_SIZE", "BACKEND_CHUNK_SIZE"),
    )
    CHUNK_OVERLAP: int = Field(
        default=200,
        validation_alias=AliasChoices("CHUNK_OVERLAP", "BACKEND_CHUNK_OVERLAP"),
    )
    EMBEDDING_MODEL_NAME: str = Field(
        default="all-MiniLM-L6-v2",
        validation_alias=AliasChoices(
            "EMBEDDING_MODEL_NAME", "BACKEND_EMBEDDING_MODEL_NAME"
        ),
    )
    FAISS_INDEX_CLOUDINARY_FOLDER: str = Field(
        default="faiss_indexes",
        validation_alias=AliasChoices(
            "FAISS_INDEX_CLOUDINARY_FOLDER", "BACKEND_FAISS_INDEX_CLOUDINARY_FOLDER"
        ),
    )
    INGESTION_STUCK_THRESHOLD_MINUTES: int = Field(
        default=15,
        validation_alias=AliasChoices(
            "INGESTION_STUCK_THRESHOLD_MINUTES",
            "BACKEND_INGESTION_STUCK_THRESHOLD_MINUTES",
        ),
    )

    # Groq & Reasoning Agent Settings
    GROQ_API_KEY: str = Field(
        default="",
        validation_alias=AliasChoices("GROQ_API_KEY", "BACKEND_GROQ_API_KEY"),
    )
    REASONING_MODEL_NAME: str = Field(
        default="llama-3.1-8b-instant",
        validation_alias=AliasChoices(
            "REASONING_MODEL_NAME", "BACKEND_REASONING_MODEL_NAME"
        ),
    )
    AGENT_TIMEOUT_SECONDS: int = Field(
        default=15,
        validation_alias=AliasChoices(
            "AGENT_TIMEOUT_SECONDS", "BACKEND_AGENT_TIMEOUT_SECONDS"
        ),
    )
    AGGREGATOR_MODEL_NAME: str = Field(
        default="llama-3.3-70b-versatile",
        validation_alias=AliasChoices(
            "AGGREGATOR_MODEL_NAME", "BACKEND_AGGREGATOR_MODEL_NAME"
        ),
    )
    DEFAULT_AGENT_WEIGHTS: Dict[str, float] = Field(
        default={
            "logical": 1.0,
            "rational": 1.0,
            "practical": 1.0,
            "spiritual": 1.0,
            "skeptical": 1.0,
        },
        validation_alias=AliasChoices(
            "DEFAULT_AGENT_WEIGHTS", "BACKEND_DEFAULT_AGENT_WEIGHTS"
        ),
    )
    CONFIDENCE_WEIGHT_RETRIEVAL: float = Field(
        default=0.35,
        validation_alias=AliasChoices(
            "CONFIDENCE_WEIGHT_RETRIEVAL", "BACKEND_CONFIDENCE_WEIGHT_RETRIEVAL"
        ),
    )
    CONFIDENCE_WEIGHT_EVIDENCE: float = Field(
        default=0.45,
        validation_alias=AliasChoices(
            "CONFIDENCE_WEIGHT_EVIDENCE", "BACKEND_CONFIDENCE_WEIGHT_EVIDENCE"
        ),
    )
    CONFIDENCE_WEIGHT_AGREEMENT: float = Field(
        default=0.20,
        validation_alias=AliasChoices(
            "CONFIDENCE_WEIGHT_AGREEMENT", "BACKEND_CONFIDENCE_WEIGHT_AGREEMENT"
        ),
    )
    MAX_CHAT_HISTORY_MESSAGES: int = Field(
        default=10,
        validation_alias=AliasChoices(
            "MAX_CHAT_HISTORY_MESSAGES", "BACKEND_MAX_CHAT_HISTORY_MESSAGES"
        ),
    )

    # Rate Limiting Settings
    RATE_LIMIT_AUTH_PER_MINUTE: str = Field(
        default="10/minute",
        validation_alias=AliasChoices(
            "RATE_LIMIT_AUTH_PER_MINUTE", "BACKEND_RATE_LIMIT_AUTH_PER_MINUTE"
        ),
    )
    RATE_LIMIT_QUESTIONS_PER_MINUTE: str = Field(
        default="20/minute",
        validation_alias=AliasChoices(
            "RATE_LIMIT_QUESTIONS_PER_MINUTE", "BACKEND_RATE_LIMIT_QUESTIONS_PER_MINUTE"
        ),
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("ALLOWED_ORIGINS", "ALLOWED_DOCUMENT_TYPES", mode="before")
    @classmethod
    def parse_list_from_string(cls, value: Union[str, List[str]]) -> List[str]:
        """Parse comma-separated strings into a list of strings."""
        if isinstance(value, str) and not value.strip().startswith("["):
            return [item.strip() for item in value.split(",") if item.strip()]
        elif isinstance(value, list):
            return value
        return value

    @model_validator(mode="after")
    def validate_confidence_weights(self) -> "Settings":
        """Validate that confidence weights are non-negative and sum to 1.0 within floating-point tolerance."""
        w_ret = self.CONFIDENCE_WEIGHT_RETRIEVAL
        w_ev = self.CONFIDENCE_WEIGHT_EVIDENCE
        w_agr = self.CONFIDENCE_WEIGHT_AGREEMENT
        if w_ret < 0 or w_ev < 0 or w_agr < 0:
            raise ValueError(
                f"Confidence weights must be non-negative: retrieval={w_ret}, evidence={w_ev}, agreement={w_agr}"
            )
        total = w_ret + w_ev + w_agr
        if abs(total - 1.0) > 1e-4:
            raise ValueError(
                f"Confidence weights must sum to 1.0 (got {total:.4f}): retrieval={w_ret}, evidence={w_ev}, agreement={w_agr}"
            )
        return self


settings = Settings()
