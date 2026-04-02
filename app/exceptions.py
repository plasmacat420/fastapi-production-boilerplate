from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(self, status_code: int, detail: str, error_code: str = "ERROR"):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code
        super().__init__(detail)


class AuthException(AppException):
    def __init__(self, detail: str = "Authentication required"):
        super().__init__(status_code=401, detail=detail, error_code="UNAUTHORIZED")


class ForbiddenException(AppException):
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(status_code=403, detail=detail, error_code="FORBIDDEN")


class NotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail, error_code="NOT_FOUND")


class ConflictException(AppException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=409, detail=detail, error_code="CONFLICT")


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.detail,
            "status_code": exc.status_code,
        },
    )
