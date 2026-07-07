from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppException
from app.middleware.correlation_id import get_request_id


def register_error_handlers(app: FastAPI) -> None:
    """Register global exception handlers returning a consistent JSON error envelope."""

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        req_id = get_request_id()
        headers = {"X-Request-ID": req_id} if req_id and req_id != "-" else {}
        return JSONResponse(
            status_code=exc.status_code,
            headers=headers,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                },
                "detail": exc.message,
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        req_id = get_request_id()
        headers = {"X-Request-ID": req_id} if req_id and req_id != "-" else {}
        if exc.headers:
            headers.update(exc.headers)

        code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            409: "CONFLICT",
            422: "VALIDATION_ERROR",
            429: "RATE_LIMIT_EXCEEDED",
            500: "INTERNAL_SERVER_ERROR",
            502: "EXTERNAL_SERVICE_ERROR",
            503: "SERVICE_UNAVAILABLE",
        }
        code = code_map.get(exc.status_code, f"HTTP_{exc.status_code}")
        message = str(exc.detail) if exc.detail else "HTTP error occurred"
        return JSONResponse(
            status_code=exc.status_code,
            headers=headers,
            content={
                "error": {
                    "code": code,
                    "message": message,
                    "details": None,
                },
                "detail": exc.detail,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        req_id = get_request_id()
        headers = {"X-Request-ID": req_id} if req_id and req_id != "-" else {}
        return JSONResponse(
            status_code=422,
            headers=headers,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": exc.errors(),
                },
                "detail": exc.errors(),
            },
        )

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exception_handler(
        request: Request, exc: RateLimitExceeded
    ) -> JSONResponse:
        req_id = get_request_id()
        headers = {"X-Request-ID": req_id} if req_id and req_id != "-" else {}
        message = f"Rate limit exceeded: {exc.detail}"
        return JSONResponse(
            status_code=429,
            headers=headers,
            content={
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": message,
                    "details": str(exc.detail),
                },
                "detail": message,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        req_id = get_request_id()
        headers = {"X-Request-ID": req_id} if req_id and req_id != "-" else {}
        message = "An unexpected internal server error occurred."
        return JSONResponse(
            status_code=500,
            headers=headers,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": message,
                    "details": str(exc) if app.debug else None,
                },
                "detail": message,
            },
        )
