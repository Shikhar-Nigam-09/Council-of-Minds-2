from unittest.mock import MagicMock, patch

import pytest

from app.core.config import settings
from app.services.storage.cloudinary_client import CloudinaryStorageClient


@pytest.fixture
def real_cloudinary_client(monkeypatch):
    """Fixture providing a CloudinaryStorageClient configured for real development mode."""
    monkeypatch.setattr(settings, "ENVIRONMENT", "development")
    monkeypatch.setattr(settings, "CLOUDINARY_CLOUD_NAME", "real_test_cloud")
    monkeypatch.setattr(settings, "CLOUDINARY_API_KEY", "real_test_key")
    monkeypatch.setattr(settings, "CLOUDINARY_API_SECRET", "real_test_secret")

    with patch("cloudinary.config"):
        client = CloudinaryStorageClient()
        assert client.configured is True
        return client


@pytest.mark.asyncio
async def test_real_documents_public_id_not_mock(real_cloudinary_client):
    """Prove that a real documents/... public ID is NOT automatically treated as mock."""
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"%PDF-1.4 real pdf content"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Call with a public ID starting with documents/
        content = await real_cloudinary_client.get_file_bytes("documents/doc-123.pdf")
        assert content == b"%PDF-1.4 real pdf content"
        assert content != b"Mock file content for testing"
        mock_get.assert_called_once()
        # Verify it generated the Cloudinary raw resource URL
        called_url = mock_get.call_args[0][0]
        assert "res.cloudinary.com" in called_url
        assert "documents/doc-123.pdf" in called_url


@pytest.mark.asyncio
async def test_real_faiss_indexes_public_id_not_mock(real_cloudinary_client):
    """Prove that a real faiss_indexes/... public ID is NOT automatically treated as mock."""
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"FAISS real index bytes"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        content = await real_cloudinary_client.get_file_bytes(
            "faiss_indexes/user-1/index.faiss"
        )
        assert content == b"FAISS real index bytes"
        assert content != b"Mock file content for testing"
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        assert "res.cloudinary.com" in called_url
        assert "faiss_indexes/user-1/index.faiss" in called_url


@pytest.mark.asyncio
async def test_real_deletion_calls_cloudinary(real_cloudinary_client):
    """Prove that real deletion calls cloudinary.uploader.destroy with resource_type='raw'."""
    with patch("cloudinary.uploader.destroy") as mock_destroy:
        mock_destroy.return_value = {"result": "ok"}

        res1 = await real_cloudinary_client.delete_file("documents/doc-456")
        res2 = await real_cloudinary_client.delete_file(
            "faiss_indexes/user-1/index.faiss"
        )

        assert res1 is True
        assert res2 is True
        assert mock_destroy.call_count == 2
        mock_destroy.assert_any_call("documents/doc-456", resource_type="raw")
        mock_destroy.assert_any_call(
            "faiss_indexes/user-1/index.faiss", resource_type="raw"
        )


@pytest.mark.asyncio
async def test_test_mode_still_uses_mock_storage(monkeypatch):
    """Prove that test mode still uses _mock_storage."""
    monkeypatch.setattr(settings, "ENVIRONMENT", "testing")
    client = CloudinaryStorageClient()

    file_content = b"Test mode in-memory bytes"
    public_id, secure_url = await client.upload_file(
        file_content, "mock_test.txt", folder="documents"
    )

    assert public_id in CloudinaryStorageClient._mock_storage
    assert secure_url in CloudinaryStorageClient._mock_storage
    assert await client.get_file_bytes(secure_url) == file_content
    assert await client.get_file_bytes(public_id) == file_content

    del_res = await client.delete_file(public_id)
    assert del_res is True
    assert public_id not in CloudinaryStorageClient._mock_storage


@pytest.mark.asyncio
async def test_unknown_storage_reference_raises_error_in_development(
    real_cloudinary_client,
):
    """Prove that unknown storage references do NOT return mock content in development, but raise an error."""
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.side_effect = Exception("HTTP 404 Not Found")

        with pytest.raises(RuntimeError) as exc_info:
            await real_cloudinary_client.get_file_bytes("documents/nonexistent_doc.pdf")

        assert "Failed to download file" in str(exc_info.value)
