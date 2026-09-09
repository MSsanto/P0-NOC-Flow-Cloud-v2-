from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.errors import AppError, ProblemDetails
from app.db.session import get_db_session
from app.modules.incidents.application.services import (
    IncidentService,
    IncidentStartedAtInFutureError,
)
from app.modules.incidents.infrastructure.repository import SqlAlchemyIncidentRepository
from app.modules.incidents.presentation.schemas import (
    IncidentCreateRequest,
    IncidentResponse,
)
from app.modules.tenancy.application.context import RequestContext
from app.modules.tenancy.presentation.dependencies import get_request_context

router = APIRouter(prefix="/incidents", tags=["incidents"])


def _service(session: Session) -> IncidentService:
    return IncidentService(SqlAlchemyIncidentRepository(session))


@router.get("", response_model=list[IncidentResponse])
def list_incidents(
    session: Annotated[Session, Depends(get_db_session)],
    context: Annotated[RequestContext, Depends(get_request_context)],
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
    responses={422: {"model": ProblemDetails}},
)
def create_incident(
    payload: IncidentCreateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    context: Annotated[RequestContext, Depends(get_request_context)],
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


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
    responses={404: {"model": ProblemDetails}},
)
def get_incident(
    incident_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    context: Annotated[RequestContext, Depends(get_request_context)],
) -> IncidentResponse:
    incident = _service(session).get_incident(context.tenant_id, incident_id)
    if incident is None:
        raise AppError(
            status_code=404,
            title="Incident not found",
            detail="The requested incident was not found in the active tenant.",
            code="INCIDENT_NOT_FOUND",
            problem_slug="incident-not-found",
        )
    return IncidentResponse.model_validate(incident, from_attributes=True)
