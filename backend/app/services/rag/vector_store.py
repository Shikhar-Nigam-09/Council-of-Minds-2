import json
import logging
import os
import shutil
import tempfile
import uuid
from typing import List, Optional, Tuple

import faiss
import numpy as np

from app.core.config import settings
from app.services.storage.storage_interface import StorageInterface

logger = logging.getLogger(__name__)


def get_cache_dir(user_id: str | uuid.UUID) -> str:
    """Get local disk cache directory for a user's FAISS index."""
    path = os.path.join(tempfile.gettempdir(), "faiss_cache", str(user_id))
    os.makedirs(path, exist_ok=True)
    return path


def _is_metadata_compatible(metadata: dict) -> bool:
    """Verify whether a stored FAISS metadata dict matches current embedding configuration and schema version."""
    if not isinstance(metadata, dict):
        return False
    if settings.ENVIRONMENT.lower() not in ["test", "testing"]:
        if metadata.get("dimension") != settings.EMBEDDING_DIMENSION:
            return False
    else:
        if (
            not isinstance(metadata.get("dimension"), int)
            or metadata.get("dimension") <= 0
        ):
            return False
    if metadata.get("embedding_version") != "2.1_remote_bge":
        return False
    if metadata.get("embedding_provider") != settings.EMBEDDING_PROVIDER:
        return False
    if metadata.get("embedding_model") != settings.EMBEDDING_MODEL_NAME:
        return False
    return True


def build_index(dimension: Optional[int] = None) -> Tuple[faiss.IndexIDMap, dict]:
    """Create a brand new empty FAISS IndexIDMap with inner product (cosine similarity) and current metadata."""
    dim = dimension if dimension is not None else settings.EMBEDDING_DIMENSION
    flat_index = faiss.IndexFlatIP(dim)
    id_map_index = faiss.IndexIDMap(flat_index)
    metadata = {
        "id_to_uuid": {},
        "uuid_to_id": {},
        "next_id": 1,
        "dimension": dim,
        "embedding_provider": settings.EMBEDDING_PROVIDER,
        "embedding_model": settings.EMBEDDING_MODEL_NAME,
        "embedding_version": "2.1_remote_bge",
    }
    return id_map_index, metadata


async def save_index(
    user_id: str | uuid.UUID,
    index: faiss.IndexIDMap,
    metadata: dict,
    storage_client: StorageInterface,
) -> None:
    """Save FAISS index and metadata to local cache and upload to Cloudinary."""
    cache_dir = get_cache_dir(user_id)
    index_path = os.path.join(cache_dir, "index.faiss")
    meta_path = os.path.join(cache_dir, "metadata.json")

    # Save locally
    faiss.write_index(index, index_path)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    # Upload index.faiss to Cloudinary
    with open(index_path, "rb") as f:
        index_bytes = f.read()
    await storage_client.upload_file(
        file_bytes=index_bytes,
        filename="index.faiss",
        folder=f"{settings.FAISS_INDEX_CLOUDINARY_FOLDER}/{user_id}",
    )

    # Upload metadata.json to Cloudinary
    with open(meta_path, "rb") as f:
        meta_bytes = f.read()
    await storage_client.upload_file(
        file_bytes=meta_bytes,
        filename="metadata.json",
        folder=f"{settings.FAISS_INDEX_CLOUDINARY_FOLDER}/{user_id}",
    )
    logger.info(
        f"Saved and uploaded FAISS index for user {user_id} (total={index.ntotal})"
    )


async def load_index(
    user_id: str | uuid.UUID,
    storage_client: StorageInterface,
) -> Tuple[Optional[faiss.IndexIDMap], Optional[dict]]:
    """Load FAISS index and metadata from local cache or lazy-load from Cloudinary."""
    cache_dir = get_cache_dir(user_id)
    index_path = os.path.join(cache_dir, "index.faiss")
    meta_path = os.path.join(cache_dir, "metadata.json")

    # 1. Check local warm cache
    if os.path.exists(index_path) and os.path.exists(meta_path):
        try:
            index = faiss.read_index(index_path)
            with open(meta_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            if _is_metadata_compatible(metadata):
                logger.debug(
                    f"Loaded warm FAISS index from local cache for user {user_id}"
                )
                return index, metadata
            else:
                logger.info(
                    f"Local cache FAISS index for user {user_id} is from an older or incompatible embedding version. Discarding."
                )
        except Exception as e:
            logger.warning(
                f"Corrupted local FAISS cache for user {user_id}: {str(e)}. Attempting download."
            )

    # 2. Download from Cloudinary
    try:
        index_public_id = (
            f"{settings.FAISS_INDEX_CLOUDINARY_FOLDER}/{user_id}/index.faiss"
        )
        meta_public_id = (
            f"{settings.FAISS_INDEX_CLOUDINARY_FOLDER}/{user_id}/metadata.json"
        )

        index_bytes = await storage_client.get_file_bytes(index_public_id)
        meta_bytes = await storage_client.get_file_bytes(meta_public_id)

        with open(index_path, "wb") as f:
            f.write(index_bytes)
        with open(meta_path, "wb") as f:
            f.write(meta_bytes)

        index = faiss.read_index(index_path)
        metadata = json.loads(meta_bytes.decode("utf-8"))
        if not _is_metadata_compatible(metadata):
            logger.info(
                f"Cloudinary FAISS index for user {user_id} is from an older or incompatible embedding version. Requesting rebuild from DB."
            )
            return None, None

        logger.info(
            f"Lazy-loaded FAISS index from Cloudinary for user {user_id} (total={index.ntotal})"
        )
        return index, metadata
    except Exception as e:
        logger.info(
            f"No valid FAISS index found in Cloudinary for user {user_id}: {str(e)}"
        )
        return None, None


async def add_vectors(
    user_id: str | uuid.UUID,
    index: faiss.IndexIDMap,
    metadata: dict,
    embeddings: np.ndarray,
    chunk_ids: List[str | uuid.UUID],
    storage_client: StorageInterface,
) -> Tuple[faiss.IndexIDMap, dict]:
    """Add vectors and chunk IDs to FAISS index and persist."""
    if len(chunk_ids) == 0 or embeddings.shape[0] == 0:
        return index, metadata

    # Check for any existing chunk IDs (idempotency / overwrite on retry)
    old_int_ids = []
    for cid in chunk_ids:
        cid_str = str(cid)
        if cid_str in metadata["uuid_to_id"]:
            old_id = metadata["uuid_to_id"][cid_str]
            old_int_ids.append(old_id)
            del metadata["id_to_uuid"][str(old_id)]
            del metadata["uuid_to_id"][cid_str]

    if old_int_ids:
        try:
            index.remove_ids(np.array(old_int_ids, dtype=np.int64))
            logger.debug(
                f"Removed {len(old_int_ids)} existing vector IDs before overwrite for user {user_id}"
            )
        except Exception as e:
            logger.warning(f"Failed to remove old IDs in place: {str(e)}")

    # Assign new integer IDs
    new_int_ids = []
    for cid in chunk_ids:
        cid_str = str(cid)
        int_id = metadata["next_id"]
        metadata["next_id"] += 1
        metadata["uuid_to_id"][cid_str] = int_id
        metadata["id_to_uuid"][str(int_id)] = cid_str
        new_int_ids.append(int_id)

    index.add_with_ids(embeddings, np.array(new_int_ids, dtype=np.int64))
    await save_index(user_id, index, metadata, storage_client)
    return index, metadata


async def rebuild_index_from_chunks(
    user_id: str | uuid.UUID,
    chunks: list,
    embeddings: np.ndarray,
    storage_client: StorageInterface,
) -> Tuple[faiss.IndexIDMap, dict]:
    """Rebuild a user's FAISS index from scratch from authoritative chunk rows."""
    index, metadata = build_index()
    if not chunks or len(chunks) == 0 or embeddings.shape[0] == 0:
        await delete_index(user_id, storage_client)
        return index, metadata

    chunk_ids = [c.id for c in chunks]
    return await add_vectors(
        user_id, index, metadata, embeddings, chunk_ids, storage_client
    )


async def delete_index(
    user_id: str | uuid.UUID,
    storage_client: StorageInterface,
) -> None:
    """Delete FAISS index assets from Cloudinary and clear local cache."""
    cache_dir = get_cache_dir(user_id)
    shutil.rmtree(cache_dir, ignore_errors=True)

    try:
        index_public_id = (
            f"{settings.FAISS_INDEX_CLOUDINARY_FOLDER}/{user_id}/index.faiss"
        )
        await storage_client.delete_file(index_public_id)
    except Exception:
        pass

    try:
        meta_public_id = (
            f"{settings.FAISS_INDEX_CLOUDINARY_FOLDER}/{user_id}/metadata.json"
        )
        await storage_client.delete_file(meta_public_id)
    except Exception:
        pass

    logger.info(f"Deleted FAISS index assets for user {user_id}")


def search(
    user_id: str | uuid.UUID,
    index: Optional[faiss.IndexIDMap],
    metadata: Optional[dict],
    query_vector: np.ndarray,
    top_k: int = 5,
) -> dict:
    """Search FAISS index for top_k most similar chunks."""
    if index is None or metadata is None or index.ntotal == 0:
        return {
            "status": "no_index",
            "results": [],
            "message": "No indexed documents available for this user.",
        }

    k = min(top_k, index.ntotal)
    distances, indices = index.search(query_vector, k)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx != -1 and str(idx) in metadata["id_to_uuid"]:
            chunk_uuid = metadata["id_to_uuid"][str(idx)]
            results.append(
                {
                    "chunk_id": chunk_uuid,
                    "score": float(dist),
                }
            )

    return {
        "status": "success",
        "results": results,
    }
