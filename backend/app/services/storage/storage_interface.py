from abc import ABC, abstractmethod
from typing import Tuple


class StorageInterface(ABC):
    """Abstract base class for file and vector storage backends."""

    @abstractmethod
    async def upload_file(
        self, file_bytes: bytes, filename: str, folder: str = "documents"
    ) -> Tuple[str, str]:
        """Upload file bytes to storage. Returns (public_id, secure_url)."""
        pass

    @abstractmethod
    async def delete_file(self, public_id: str) -> bool:
        """Delete file from storage by public_id. Returns True if deleted or not found."""
        pass

    @abstractmethod
    async def get_file_bytes(self, secure_url: str) -> bytes:
        """Fetch raw bytes of stored file from secure_url."""
        pass
