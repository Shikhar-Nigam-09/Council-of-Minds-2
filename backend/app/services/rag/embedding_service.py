import logging
from typing import List, Optional

import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Singleton service for loading sentence-transformers model and generating vector embeddings."""

    _instance: Optional["EmbeddingService"] = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _load_model(self):
        if self._model is None:
            logger.info(
                f"Loading sentence-transformers embedding model: {settings.EMBEDDING_MODEL_NAME}"
            )
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
            logger.info("Embedding model loaded successfully.")

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Generate normalized embeddings for a list of text strings.

        Returns: np.ndarray of shape (len(texts), 384) with float32 dtype, L2 normalized.
        """
        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        self._load_model()
        try:
            # normalize_embeddings=True ensures cosine similarity equals inner product / L2 similarity
            embeddings = self._model.encode(
                texts, convert_to_numpy=True, normalize_embeddings=True
            )
            return embeddings.astype(np.float32)
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise RuntimeError(f"Embedding generation failed: {str(e)}")

    def embed_query(self, text: str) -> np.ndarray:
        """Generate normalized embedding for a single query string.

        Returns: np.ndarray of shape (1, 384) with float32 dtype.
        """
        return self.embed_texts([text])


# Module-level singleton accessor
embedding_service = EmbeddingService()
