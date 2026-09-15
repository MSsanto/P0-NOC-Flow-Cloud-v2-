from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.errors import AppError, ProblemDetails
from app.db.session import get_db_session
from app.modules.incidents.application.services import (
    IncidentAlreadyNormalizedError,
    IncidentCannotBeUpdatedError,
    IncidentNotFoundError,
    IncidentService,
    IncidentStartedAtInFutureError,
)
from app.modules.incidents.infrastructure.repository import SqlAlchemyIncidentRepository
from app.modules.incidents.presentation.schemas import (
    IncidentCreateRequest,
    IncidentEventResponse,
    IncidentNormalizeRequest,
    IncidentResponse,
    IncidentUpdateRequest,
)
from app.modules.tenancy.application.context import RequestContext
from app.modules.tenancy.application.security import Permission
from app.modules.tenancy.presentation.dependencies import require_permission

router = APIRouter(prefix="/incidents", tags=["incidents"])


def _service(session: Session) -> IncidentService:
    return IncidentService(SqlAlchemyIncidentRepository(session))


def _not_found_error() -> AppError:
    return AppError(
        status_code=404,
        title="Incident not found",
        detail="The requested incident was not found in the active tenant.",
        code="INCIDENT_NOT_FOUND",
        problem_slug="incident-not-found",
    )


@router.get("", response_model=list[IncidentResponse])
def list_incidents(
    session: Annotated[Session, Depends(get_db_session)],
    context: Annotated[
        RequestContext, Depends(require_permission(Permission.INCIDENT_READ))
    ],
) -> list[IncidentResponse]:
    incidents = _service(session).list_incidents(context.tenant_id)
    return [
        IncidentResponse.model_validate(item, from_attributes=True)
        for item in incidents
    ]


@router.post(
    "",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
    responses={401: {"model": ProblemDetails}, 403: {"model": ProblemDetails}, 422: {"model": ProblemDetails}},
)
def create_incident(
    payload: IncidentCreateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    context: Annotated[
        RequestContext, Depends(require_permission(Permission.INCIDENT_CREATE))
    ],
) -> IncidentResponse:
    try:
        incident = _service(session).create_incident(
            tenant_id=context.tenant_id,
            actor_subject=context.actor_subject,
            **payload.model_dump(),
        )
    except IncidentStartedAtInFutureError as exc:
        raise AppError(
            status_code=422,
            title="Incident validation failed",
            detail=str(exc),
            code="INCIDENT_STARTED_AT_IN_FUTURE",
            problem_slug="incident-started-at-in-future",
        ) from exc
    return IncidentResponse.model_validate(incident, from_attributes=True)


@router.post(
    "/{incident_id}/updates",
    response_model=IncidentResponse,
    responses={
        401: {"model": ProblemDetails},
        403: {"model": ProblemDetails},
        404: {"model": ProblemDetails},
        409: {"model": ProblemDetails},
        422: {"model": ProblemDetails},
    },
)
def add_incident_update(
    incident_id: UUID,
    payload: IncidentUpdateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    context: Annotated[
        RequestContext, Depends(require_permission(Permission.INCIDENT_UPDATE))
    ],
) -> IncidentResponse:
    try:
        incident = _service(session).add_update(
            tenant_id=context.tenant_id,
            incident_id=incident_id,
            actor_subject=context.actor_subject,
            message=payload.message,
        )
    except IncidentNotFoundError as exc:
        raise _not_found_error() from exc
    except IncidentCannotBeUpdatedError as exc:
        raise AppError(
            status_code=409,
            title="Incident cannot be updated",
            detail=str(exc),
            code="INCIDENT_NOT_ACTIVE",
            problem_slug="incident-not-active",
        ) from exc
    return IncidentResponse.model_validate(incident, from_attributes=True)


@router.post(
    "/{incident_id}/normalize",
    response_model=IncidentResponse,
    responses={
        401: {"model": ProblemDetails},
        403: {"model": ProblemDetails},
        404: {"model": ProblemDetails},
        409: {"model": ProblemDetails},
        422: {"model": ProblemDetails},
    },
)
def normalize_incident(
    incident_id: UUID,
    payload: IncidentNormalizeRequest,
    session: Annotated[Session, Depends(get_db_session)],
    context: Annotated[
        RequestContext, Depends(require_permission(Permission.INCIDENT_NORMALIZE))
    ],
) -> IncidentResponse:
    try:
        incident = _service(session).normalize_incident(
            tenant_id=context.tenant_id,
            incident_id=incident_id,
            actor_subject=context.actor_subject,
            note=payload.note,
        )
    except IncidentNotFoundError as exc:
        raise _not_found_error() from exc
    except IncidentAlreadyNormalizedError as exc:
        raise AppError(
            status_code=409,
            title="Incident already normalized",
            detail=str(exc),
            code="INCIDENT_ALREADY_NORMALIZED",
            problem_slug="incident-already-normalized",
        ) from exc
    return IncidentResponse.model_validate(incident, from_attributes=True)


@router.get(
    "/{incident_id}/timeline",
    response_model=list[IncidentEventResponse],
    responses={401: {"model": ProblemDetails}, 403: {"model": ProblemDetails}, 404: {"model": ProblemDetails}},
)
def get_incident_timeline(
    incident_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    context: Annotated[
        RequestContext, Depends(require_permission(Permission.INCIDENT_READ))
    ],
) -> list[IncidentEventResponse]:
    try:
        events = _service(session).list_timeline(context.tenant_id, incident_id)
    except IncidentNotFoundError as exc:
        raise _not_found_error() from exc
    return [
        IncidentEventResponse.model_validate(item, from_attributes=True)
        for item in events
    ]


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
    responses={401: {"model": ProblemDetails}, 403: {"model": ProblemDetails}, 404: {"model": ProblemDetails}},
)
def get_incident(
    incident_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    context: Annotated[
        RequestContext, Depends(require_permission(Permission.INCIDENT_READ))
    ],
) -> IncidentResponse:
    incident = _service(session).get_incident(context.tenant_id, incident_id)
    if incident is None:
        raise _not_found_error()
    return IncidentResponse.model_validate(incident, from_attributes=True)
