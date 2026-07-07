import logging
import re
from typing import List

import numpy as np

from app.schemas.council_response import ChunkRef
from app.services.rag.embedding_service import embedding_service

logger = logging.getLogger(__name__)


def compute_evidence_coverage(
    aggregated_answer: str, retrieved_chunks: List[ChunkRef]
) -> float:
    """
    Computes the Evidence Coverage signal using an embedding-based grounding heuristic.

    Important Semantic Note:
    This metric measures **semantic evidence support** rather than factual correctness.
    It evaluates the degree to which the statements and themes in the synthesized answer
    align semantically with the text of the retrieved document chunks. High coverage indicates
    that the answer discusses topics well-supported by the retrieved evidence; it does not
    guarantee that every granular fact or number is incontrovertibly true.

    Methodology:
    1. If the retrieved chunks list is empty or the aggregated answer is empty/whitespace,
       returns 0.0 immediately.
    2. We segment the aggregated answer into individual sentences or clauses using punctuation delimiters.
    3. We embed each sentence and all retrieved chunk texts using our L2-normalized MiniLM embedding model.
    4. For each sentence s_j, we compute its cosine similarity against all chunk embeddings C_i:
           sim(s_j, C_i) = dot(embed(s_j), embed(C_i))
       We find the maximum similarity across all chunks:
           max_sim(s_j) = max_i(sim(s_j, C_i))
       and clamp it to [0.0, 1.0].
    5. Evidence Coverage is the arithmetic mean of these maximum similarities across all sentences:
           Evidence Coverage = (1 / K) * sum(max_sim(s_j)) for j=1..K
    """
    if not retrieved_chunks or len(retrieved_chunks) == 0:
        logger.debug("Evidence Coverage: 0.0 (empty retrieval list)")
        return 0.0

    if not aggregated_answer or not aggregated_answer.strip():
        logger.debug("Evidence Coverage: 0.0 (empty aggregated answer)")
        return 0.0

    # Split answer into meaningful sentences/clauses
    raw_sentences = re.split(r"[.!?\n]+", aggregated_answer)
    sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 10]

    # If no sentences > 10 chars, fallback to embedding the whole string as one chunk
    if not sentences:
        sentences = [aggregated_answer.strip()]

    chunk_texts = [
        chunk.content.strip()
        for chunk in retrieved_chunks
        if chunk.content and chunk.content.strip()
    ]
    if not chunk_texts:
        logger.debug("Evidence Coverage: 0.0 (all chunk contents empty)")
        return 0.0

    try:
        # Embed sentences (shape: K x 384) and chunks (shape: N x 384), both L2 normalized
        sentence_embs = embedding_service.embed_texts(sentences)
        chunk_embs = embedding_service.embed_texts(chunk_texts)

        # Compute cosine similarity matrix (shape: K x N) via dot product
        sim_matrix = np.dot(sentence_embs, chunk_embs.T)

        # Find max similarity for each sentence
        max_sims = np.max(sim_matrix, axis=1)
        clamped_sims = np.clip(max_sims, 0.0, 1.0)

        mean_coverage = float(np.mean(clamped_sims))
        logger.debug(
            f"Evidence Coverage: {mean_coverage:.4f} across {len(sentences)} sentences and {len(chunk_texts)} chunks"
        )
        return round(mean_coverage, 4)
    except Exception as exc:
        logger.error(
            f"Error computing evidence coverage: {exc}. Falling back to 0.0.",
            exc_info=True,
        )
        return 0.0
