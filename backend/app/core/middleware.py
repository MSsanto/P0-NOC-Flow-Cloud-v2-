import re
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import log_http_request
from app.core.request_context import reset_request_id, set_request_id

_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")


def _resolve_request_id(candidate: str | None) -> str:
    if candidate and _REQUEST_ID_PATTERN.fullmatch(candidate):
        return candidate
    return str(uuid4())


def register_middleware(app: FastAPI) -> None:
    settings = get_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request_id = _resolve_request_id(request.headers.get("X-Request-ID"))
        request.state.request_id = request_id
        token = set_request_id(request_id)
        started = perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            log_http_request(
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=500,
                duration_ms=(perf_counter() - started) * 1000,
            )
            raise
        finally:
            reset_request_id(token)
        response.headers["X-Request-ID"] = request_id
        log_http_request(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=(perf_counter() - started) * 1000,
        )
        return response
