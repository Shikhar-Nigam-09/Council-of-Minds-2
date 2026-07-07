import io
import logging

from pypdf import PdfReader

logger = logging.getLogger(__name__)


class TextExtractionError(Exception):
    """Exception raised when text extraction fails."""

    pass


def extract_text(file_bytes: bytes, file_type: str, filename: str) -> str:
    """Extract plain text from file bytes based on MIME type or filename extension.

    Supported formats: PDF, TXT, Markdown.
    """
    try:
        ext = filename.lower().split(".")[-1] if "." in filename else ""
        is_pdf = file_type == "application/pdf" or ext == "pdf"

        if is_pdf:
            reader = PdfReader(io.BytesIO(file_bytes))
            text_parts = []
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            full_text = "\n\n".join(text_parts).strip()
            if not full_text:
                raise TextExtractionError(
                    "No extractable text found in PDF (may be scanned or empty)."
                )
            return full_text
        else:
            # Plain text or Markdown
            try:
                text = file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                text = file_bytes.decode("latin-1", errors="replace")
            text = text.strip()
            if not text:
                raise TextExtractionError("File content is empty.")
            return text
    except TextExtractionError:
        raise
    except Exception as e:
        logger.error(f"Failed to extract text from {filename} ({file_type}): {str(e)}")
        raise TextExtractionError(f"Extraction failed: {str(e)}")
