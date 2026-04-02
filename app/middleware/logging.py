import time
import uuid

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start_time = time.perf_counter()

        with logger.contextualize(request_id=request_id):
            logger.info(
                "Request started",
                method=request.method,
                path=request.url.path,
                client=request.client.host if request.client else "unknown",
            )

            response = await call_next(request)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

            logger.info(
                "Request completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
            )

        response.headers["X-Request-ID"] = request_id
        return response
