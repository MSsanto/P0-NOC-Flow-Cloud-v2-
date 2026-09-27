import re
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import get_logger

_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
_TRACEPARENT_PATTERN = re.compile(
    r"^([0-9a-f]{2})-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})$",
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
    if not match:
        return None

    version, trace_id, parent_id, _flags = (part.lower() for part in match.groups())
    if version == "ff" or trace_id == "0" * 32 or parent_id == "0" * 16:
        return None
    return trace_id


def _log_request(
    request: Request,
    *,
    request_id: str,
    trace_id: str | None,
    status_code: int,
    started_at: float,
    unexpected_error: bool = False,
) -> None:
    route = request.scope.get("route")
    route_path = getattr(route, "path", request.url.path)
    duration_ms = round((perf_counter() - started_at) * 1000, 3)
    extra = {
        "request_id": request_id,
        "trace_id": trace_id,
        "route": route_path,
        "method": request.method,
        "status_code": status_code,
        "duration_ms": duration_ms,
    }

    if unexpected_error:
        logger.exception("http_request", extra=extra)
    elif status_code >= 500:
        logger.error("http_request", extra=extra)
    elif status_code >= 400:
        logger.warning("http_request", extra=extra)
    else:
        logger.info("http_request", extra=extra)


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

        try:
            response = await call_next(request)
        except Exception:
            _log_request(
                request,
                request_id=request_id,
                trace_id=trace_id,
                status_code=500,
                started_at=started_at,
                unexpected_error=True,
            )
            raise

        response.headers["X-Request-ID"] = request_id
        _log_request(
            request,
            request_id=request_id,
            trace_id=trace_id,
            status_code=response.status_code,
            started_at=started_at,
        )
        return response
