from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

PROBLEM_BASE_URL = "https://nocflow.example/problems"


class ValidationIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str
    code: str
    message: str


class ProblemDetails(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    title: str
    status: int
    detail: str
    instance: str
    code: str
    request_id: str
    errors: list[ValidationIssue] | None = None


class AppError(Exception):
    def __init__(
        self,
        *,
        status_code: int,
        title: str,
        detail: str,
        code: str,
        problem_slug: str,
    ) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.title = title
        self.detail = detail
        self.code = code
        self.problem_type = f"{PROBLEM_BASE_URL}/{problem_slug}"


class DependencyUnavailableError(AppError):
    def __init__(self, detail: str = "A required dependency is unavailable.") -> None:
        super().__init__(
            status_code=503,
            title="Dependency unavailable",
            detail=detail,
            code="DEPENDENCY_UNAVAILABLE",
            problem_slug="dependency-unavailable",
        )


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


def _problem_payload(
    request: Request,
    *,
    status: int,
    title: str,
    detail: str,
    code: str,
    problem_type: str,
    errors: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "type": problem_type,
        "title": title,
        "status": status,
        "detail": detail,
        "instance": request.url.path,
        "code": code,
        "request_id": _request_id(request),
    }
    if errors:
        payload["errors"] = errors
    return payload


def _field_from_location(location: tuple[Any, ...]) -> str:
    meaningful = [str(part) for part in location if part not in {"body", "query", "path", "header"}]
    return ".".join(meaningful) or "request"


def _validation_code(error_type: str) -> str:
    return error_type.replace(".", "_").replace("-", "_").upper()


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        media_type="application/problem+json",
        content=_problem_payload(
            request,
            status=exc.status_code,
            title=exc.title,
            detail=exc.detail,
            code=exc.code,
            problem_type=exc.problem_type,
        ),
    )


async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = [
        {
            "field": _field_from_location(error["loc"]),
            "code": _validation_code(error["type"]),
            "message": error["msg"],
        }
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        media_type="application/problem+json",
        content=_problem_payload(
            request,
            status=422,
            title="Request validation failed",
            detail="Request payload or parameters are invalid.",
            code="REQUEST_VALIDATION_ERROR",
            problem_type=f"{PROBLEM_BASE_URL}/request-validation",
            errors=errors,
        ),
    )


async def unexpected_error_handler(request: Request, _exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        media_type="application/problem+json",
        content=_problem_payload(
            request,
            status=500,
            title="Internal server error",
            detail="An unexpected error occurred.",
            code="INTERNAL_ERROR",
            problem_type=f"{PROBLEM_BASE_URL}/internal-error",
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unexpected_error_handler)
