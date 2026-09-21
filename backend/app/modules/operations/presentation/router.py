from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.errors import AppError, ProblemDetails
from app.db.session import get_db_session
from app.modules.operations.application.services import (
    HandoverNotFoundError,
    HandoverVersionConflictError,
    OperationsService,
    ShiftConfigurationError,
)
from app.modules.operations.infrastructure.repository import SqlAlchemyOperationsRepository
from app.modules.operations.presentation.schemas import (
    DashboardResponse,
    HandoverFinalizeRequest,
    HandoverListResponse,
    HandoverPreviewResponse,
    HandoverResponse,
)
from app.modules.tenancy.application.context import RequestContext
from app.modules.tenancy.application.security import Permission
from app.modules.tenancy.presentation.dependencies import require_permission

router = APIRouter(tags=["operations"])


def _service(session: Session) -> OperationsService:
    return OperationsService(SqlAlchemyOperationsRepository(session))


def _shift_error(exc: ShiftConfigurationError) -> AppError:
    return AppError(
        status_code=503,
        title="Shift configuration unavailable",
        detail=str(exc),
        code="SHIFT_CONFIGURATION_INVALID",
        problem_slug="shift-configuration-invalid",
    )


def _handover_not_found() -> AppError:
    return AppError(
        status_code=404,
        title="Handover not found",
        detail="The requested handover was not found in the active tenant.",
        code="HANDOVER_NOT_FOUND",
        problem_slug="handover-not-found",
    )


@router.get(
    "/dashboard/summary",
    response_model=DashboardResponse,
    responses={401: {"model": ProblemDetails}, 403: {"model": ProblemDetails}},
)
def dashboard_summary(
    session: Annotated[Session, Depends(get_db_session)],
    context: Annotated[
        RequestContext, Depends(require_permission(Permission.INCIDENT_READ))
    ],
) -> DashboardResponse:
    try:
        summary = _service(session).dashboard(context.tenant_id)
    except ShiftConfigurationError as exc:
        raise _shift_error(exc) from exc
    return DashboardResponse.model_validate(summary, from_attributes=True)


@router.get(
    "/handovers/preview",
    response_model=HandoverPreviewResponse,
    responses={401: {"model": ProblemDetails}, 403: {"model": ProblemDetails}},
)
def handover_preview(
    session: Annotated[Session, Depends(get_db_session)],
    context: Annotated[
        RequestContext, Depends(require_permission(Permission.HANDOVER_READ))
    ],
) -> HandoverPreviewResponse:
    try:
        preview = _service(session).preview(context.tenant_id)
    except ShiftConfigurationError as exc:
        raise _shift_error(exc) from exc
    return HandoverPreviewResponse.model_validate(preview, from_attributes=True)


@router.post(
    "/handovers",
    response_model=HandoverResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ProblemDetails},
        403: {"model": ProblemDetails},
        409: {"model": ProblemDetails},
        422: {"model": ProblemDetails},
    },
)
def finalize_handover(
    payload: HandoverFinalizeRequest,
    session: Annotated[Session, Depends(get_db_session)],
    context: Annotated[
        RequestContext, Depends(require_permission(Permission.HANDOVER_FINALIZE))
    ],
) -> HandoverResponse:
    try:
        handover = _service(session).finalize(
            tenant_id=context.tenant_id,
            actor_subject=context.actor_subject,
            observations=payload.observations,
        )
    except ShiftConfigurationError as exc:
        raise _shift_error(exc) from exc
    except HandoverVersionConflictError as exc:
        raise AppError(
            status_code=409,
            title="Handover version conflict",
            detail="Another handover version was finalized concurrently. Reload and try again.",
            code="HANDOVER_VERSION_CONFLICT",
            problem_slug="handover-version-conflict",
        ) from exc
    return HandoverResponse.model_validate(handover, from_attributes=True)


@router.get(
    "/handovers",
    response_model=HandoverListResponse,
    responses={401: {"model": ProblemDetails}, 403: {"model": ProblemDetails}},
)
def handover_history(
    session: Annotated[Session, Depends(get_db_session)],
    context: Annotated[
        RequestContext, Depends(require_permission(Permission.HANDOVER_READ))
    ],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 25,
) -> HandoverListResponse:
    result = _service(session).history(context.tenant_id, page, page_size)
    return HandoverListResponse.model_validate(result, from_attributes=True)


@router.get(
    "/handovers/latest",
    response_model=HandoverResponse,
    responses={
        401: {"model": ProblemDetails},
        403: {"model": ProblemDetails},
        404: {"model": ProblemDetails},
    },
)
def latest_handover(
    session: Annotated[Session, Depends(get_db_session)],
    context: Annotated[
        RequestContext, Depends(require_permission(Permission.HANDOVER_READ))
    ],
) -> HandoverResponse:
    try:
        result = _service(session).latest(context.tenant_id)
    except HandoverNotFoundError as exc:
        raise _handover_not_found() from exc
    return HandoverResponse.model_validate(result, from_attributes=True)


@router.get(
    "/handovers/{handover_id}",
    response_model=HandoverResponse,
    responses={
        401: {"model": ProblemDetails},
        403: {"model": ProblemDetails},
        404: {"model": ProblemDetails},
    },
)
def get_handover(
    handover_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    context: Annotated[
        RequestContext, Depends(require_permission(Permission.HANDOVER_READ))
    ],
) -> HandoverResponse:
    try:
        result = _service(session).get(context.tenant_id, handover_id)
    except HandoverNotFoundError as exc:
        raise _handover_not_found() from exc
    return HandoverResponse.model_validate(result, from_attributes=True)
