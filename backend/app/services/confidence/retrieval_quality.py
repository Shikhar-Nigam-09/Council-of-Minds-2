import logging
from typing import List

from app.schemas.council_response import ChunkRef

logger = logging.getLogger(__name__)


def compute_retrieval_quality(retrieved_chunks: List[ChunkRef]) -> float:
    """
    Computes the Retrieval Quality signal from retrieved document chunks.

    Normalization Formula:
    In our RAG pipeline, document chunk embeddings and query embeddings are L2-normalized
    before indexing into FAISS IndexFlatIP (Inner Product). Mathematically, the inner
    product of two L2-normalized vectors is their exact cosine similarity, ranging from
    -1.0 to +1.0. For relevant text documents, similarities typically fall between 0.0 and 1.0.

    We normalize each chunk's similarity score by clamping it to the [0.0, 1.0] range:
        s_norm = max(0.0, min(1.0, chunk.similarity_score))

    The final Retrieval Quality signal is the arithmetic mean of these normalized scores
    across all retrieved chunks:
        Retrieval Quality = (1 / N) * sum(s_norm_i) for i=1..N

    Edge Case Handling:
    If no documents were retrieved (empty retrieval list, N=0), the signal returns 0.0.
    """
    if not retrieved_chunks or len(retrieved_chunks) == 0:
        logger.debug("Retrieval Quality: 0.0 (empty retrieval list)")
        return 0.0

    clamped_scores = [
        max(0.0, min(1.0, float(chunk.similarity_score))) for chunk in retrieved_chunks
    ]
    mean_score = sum(clamped_scores) / len(clamped_scores)
    logger.debug(
        f"Retrieval Quality: {mean_score:.4f} across {len(retrieved_chunks)} chunks"
    )
    return round(mean_score, 4)
