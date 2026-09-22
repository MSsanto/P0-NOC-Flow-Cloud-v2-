import re
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import get_logger

_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
_TRACEPARENT_PATTERN = re.compile(
    r"^[0-9a-f]{2}-([0-9a-f]{32})-[0-9a-f]{16}-[0-9a-f]{2}$",
    re.IGNORECASE,
)
logger = get_logger("http")


def _resolve_request_id(candidate: str | None) -> str:
    if candidate and _REQUEST_ID_PATTERN.fullmatch(candidate):
        return candidate
    return str(uuid4())


def _resolve_trace_id(traceparent: str | None) -> str | None:
    if not traceparent:
        return None
    match = _TRACEPARENT_PATTERN.fullmatch(traceparent.strip())
    return match.group(1).lower() if match else None


def register_middleware(app: FastAPI) -> None:
    settings = get_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID", "traceparent"],
        expose_headers=["X-Request-ID"],
    )

    @app.middleware("http")
    async def observability_middleware(request: Request, call_next):
        request_id = _resolve_request_id(request.headers.get("X-Request-ID"))
        trace_id = _resolve_trace_id(request.headers.get("traceparent"))
        request.state.request_id = request_id
        request.state.trace_id = trace_id
        started_at = perf_counter()

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        route = request.scope.get("route")
        route_path = getattr(route, "path", request.url.path)
        duration_ms = round((perf_counter() - started_at) * 1000, 3)
        level = (
            logger.error
            if response.status_code >= 500
            else logger.warning
            if response.status_code >= 400
            else logger.info
        )
        level(
            "http_request",
            extra={
                "request_id": request_id,
                "trace_id": trace_id,
                "route": route_path,
                "method": request.method,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response
