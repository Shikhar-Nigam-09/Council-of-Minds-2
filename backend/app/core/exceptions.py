from typing import Any, Optional


class AppException(Exception):
    """Base exception class for all application-specific errors."""

    def __init__(
        self,
        message: str,
        code: str = "APP_ERROR",
        status_code: int = 500,
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class NotFoundError(AppException):
    """Exception raised when a requested resource is not found."""

    def __init__(
        self, message: str = "Resource not found", details: Optional[Any] = None
    ):
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404,
            details=details,
        )


class UnauthorizedError(AppException):
    """Exception raised when authentication fails or is missing."""

    def __init__(
        self,
        message: str = "Authentication required or invalid",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=401,
            details=details,
        )


class ForbiddenError(AppException):
    """Exception raised when an authenticated user lacks permission."""

    def __init__(
        self,
        message: str = "Permission denied to access this resource",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=403,
            details=details,
        )


class ValidationError(AppException):
    """Exception raised when business validation or input formatting fails."""

    def __init__(
        self, message: str = "Validation failed", details: Optional[Any] = None
    ):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details,
        )


class ExternalServiceError(AppException):
    """Exception raised when an external dependency (Groq LLM, Cloudinary, FAISS) fails."""

    def __init__(
        self,
        message: str = "External service unavailable or failed",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            code="EXTERNAL_SERVICE_ERROR",
            status_code=502,
            details=details,
        )
