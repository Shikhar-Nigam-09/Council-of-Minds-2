import logging
import sys

from app.middleware.correlation_id import get_request_id


class CorrelationIdFilter(logging.Filter):
    """Logging filter that injects the current request correlation ID into log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


def setup_logging(log_level: str = "INFO") -> None:
    """Configure structured logging for the application with request correlation ID tracking."""
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    log_format = "%(asctime)s | [req_id=%(request_id)s] | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(CorrelationIdFilter())

    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        datefmt=date_format,
        handlers=[handler],
        force=True,
    )

    # Set third-party loggers to warning or info to avoid excessive noise
    logging.getLogger("uvicorn.access").setLevel(numeric_level)
    logging.getLogger("uvicorn.error").setLevel(numeric_level)
    logging.getLogger("httpx").setLevel(logging.WARNING)
