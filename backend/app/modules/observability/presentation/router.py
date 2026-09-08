from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.errors import DependencyUnavailableError, ProblemDetails
from app.db.session import get_engine

router = APIRouter(prefix="/health", tags=["health"])


class LiveHealth(BaseModel):
    status: Literal["ok"] = "ok"


class ReadyChecks(BaseModel):
    database: Literal["up"] = "up"


class ReadyHealth(BaseModel):
    status: Literal["ready"] = "ready"
    checks: ReadyChecks


@router.get("/live", response_model=LiveHealth, summary="Liveness probe")
def liveness() -> LiveHealth:
    return LiveHealth()


@router.get(
    "/ready",
    response_model=ReadyHealth,
    responses={503: {"model": ProblemDetails, "description": "Required dependency unavailable"}},
    summary="Readiness probe",
)
def readiness() -> ReadyHealth:
    try:
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
    except (SQLAlchemyError, ModuleNotFoundError, OSError) as exc:
        raise DependencyUnavailableError("Database readiness check failed.") from exc

    return ReadyHealth(checks=ReadyChecks())
