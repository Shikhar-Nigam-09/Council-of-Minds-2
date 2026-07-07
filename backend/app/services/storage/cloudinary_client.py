import asyncio
import logging
from typing import Tuple

import cloudinary
import cloudinary.uploader
import cloudinary.utils
import httpx

from app.core.config import settings
from app.services.storage.storage_interface import StorageInterface

logger = logging.getLogger(__name__)


class CloudinaryStorageClient(StorageInterface):
    """Concrete implementation of StorageInterface using Cloudinary SDK with in-memory test fallback."""

    _mock_storage: dict[str, bytes] = {}

    def __init__(self):
        cloud_name = settings.CLOUDINARY_CLOUD_NAME
        api_key = settings.CLOUDINARY_API_KEY
        api_secret = settings.CLOUDINARY_API_SECRET

        has_valid_cloud_name = bool(cloud_name and cloud_name != "your_cloud_name")
        has_valid_api_key = bool(api_key and api_key != "your_api_key")
        has_valid_api_secret = bool(api_secret and api_secret != "your_api_secret")

        self.configured = False
        if has_valid_cloud_name and has_valid_api_key and has_valid_api_secret:
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret,
                secure=True,
            )
            self.configured = True
        else:
            logger.warning(
                "Cloudinary credentials not fully configured (missing or placeholder values). Using placeholder/mock storage mode."
            )

        logger.info(
            f"Initialized CloudinaryStorageClient: environment='{settings.ENVIRONMENT}', configured={self.configured}, mock_mode={not self.configured or settings.ENVIRONMENT.lower() in ['testing', 'test']}"
        )

    def _is_mock_mode(self, identifier: str = "") -> bool:
        """Determine if storage operation should use in-memory mock storage.

        Mock mode is enabled only if:
        - The client is not configured with valid real credentials
        - The environment is explicitly set to test/testing
        - The specific identifier (public ID or URL) is present in _mock_storage
        """
        if not self.configured or settings.ENVIRONMENT.lower() in ["testing", "test"]:
            return True
        if identifier and identifier in CloudinaryStorageClient._mock_storage:
            return True
        return False

    async def upload_file(
        self, file_bytes: bytes, filename: str, folder: str = "documents"
    ) -> Tuple[str, str]:
        """Upload raw bytes as non-image (raw) resource to Cloudinary."""
        if self._is_mock_mode():
            # Mock mode for testing or unconfigured local dev
            public_id = f"{folder}/{filename}"
            url = f"https://res.cloudinary.com/mock/raw/upload/{public_id}"
            CloudinaryStorageClient._mock_storage[public_id] = file_bytes
            CloudinaryStorageClient._mock_storage[url] = file_bytes
            logger.debug(
                f"upload_file mock storage: '{public_id}' (env='{settings.ENVIRONMENT}', configured={self.configured})"
            )
            return public_id, url

        logger.debug(
            f"upload_file real Cloudinary: '{filename}' in '{folder}' (env='{settings.ENVIRONMENT}', configured={self.configured})"
        )

        def _upload():
            return cloudinary.uploader.upload(
                file_bytes,
                resource_type="raw",
                folder=folder,
                use_filename=True,
                unique_filename=True,
            )

        try:
            result = await asyncio.to_thread(_upload)
            public_id = str(result.get("public_id", ""))
            secure_url = str(result.get("secure_url") or result.get("url", ""))
            return public_id, secure_url
        except Exception as e:
            logger.error(f"Cloudinary upload failed for {filename}: {str(e)}")
            raise RuntimeError(f"Cloudinary upload failed: {str(e)}")

    async def delete_file(self, public_id: str) -> bool:
        """Delete raw resource from Cloudinary."""
        if self._is_mock_mode(public_id):
            CloudinaryStorageClient._mock_storage.pop(public_id, None)
            logger.debug(
                f"delete_file mock storage: '{public_id}' (env='{settings.ENVIRONMENT}', configured={self.configured})"
            )
            return True

        logger.debug(
            f"delete_file real Cloudinary: '{public_id}' (env='{settings.ENVIRONMENT}', configured={self.configured})"
        )

        def _delete():
            return cloudinary.uploader.destroy(public_id, resource_type="raw")

        try:
            result = await asyncio.to_thread(_delete)
            res_status = result.get("result")
            logger.debug(
                f"delete_file Cloudinary result for '{public_id}': status={res_status}"
            )
            return res_status in ["ok", "not found"]
        except Exception as e:
            logger.error(f"Cloudinary delete failed for {public_id}: {str(e)}")
            return False

    async def get_file_bytes(self, secure_url: str) -> bytes:
        """Download file bytes from secure URL or public ID."""
        if self._is_mock_mode(secure_url):
            logger.debug(
                f"get_file_bytes mock storage: '{secure_url}' (env='{settings.ENVIRONMENT}', configured={self.configured})"
            )
            if secure_url in CloudinaryStorageClient._mock_storage:
                return CloudinaryStorageClient._mock_storage[secure_url]
            return b"Mock file content for testing"

        logger.debug(
            f"get_file_bytes real Cloudinary: '{secure_url}' (env='{settings.ENVIRONMENT}', configured={self.configured})"
        )

        download_url = secure_url
        if not (secure_url.startswith("http://") or secure_url.startswith("https://")):
            # Only a public ID was passed, generate the correct Cloudinary raw-resource URL
            try:
                download_url, _ = cloudinary.utils.cloudinary_url(
                    secure_url, resource_type="raw", secure=True
                )
            except Exception as e:
                logger.error(
                    f"Failed to generate Cloudinary URL for public ID '{secure_url}': {str(e)}"
                )
                raise RuntimeError(
                    f"Invalid storage identifier '{secure_url}': {str(e)}"
                )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(download_url)
                response.raise_for_status()
                return response.content
        except Exception as e:
            logger.error(
                f"Cloudinary download failed for identifier '{secure_url}' (url='{download_url}'): {str(e)}"
            )
            raise RuntimeError(
                f"Failed to download file '{secure_url}' from Cloudinary: {str(e)}"
            )


cloudinary_client = CloudinaryStorageClient()
