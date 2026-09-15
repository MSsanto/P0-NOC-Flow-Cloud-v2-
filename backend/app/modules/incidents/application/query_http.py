from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.db.session import get_db_session
from app.modules.incidents.application.queries import (
    IncidentListQuery,
    IncidentSortField,
    SortOrder,
)
from app.modules.incidents.application.services import IncidentService
from app.modules.incidents.domain.entities import IncidentSeverity, IncidentStatus
from app.modules.incidents.infrastructure.repository import SqlAlchemyIncidentRepository
from app.modules.incidents.presentation.schemas import (
    IncidentListResponse,
    IncidentResponse,
)
from app.modules.tenancy.application.context import RequestContext
from app.modules.tenancy.application.security import Permission
from app.modules.tenancy.presentation.dependencies import require_permission


def _as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def query_incidents(
    session: Annotated[Session, Depends(get_db_session)],
    context: Annotated[
        RequestContext, Depends(require_permission(Permission.INCIDENT_READ))
    ],
    status_filter: Annotated[IncidentStatus | None, Query(alias="status")] = None,
    severity: Annotated[IncidentSeverity | None, Query()] = None,
    started_from: Annotated[datetime | None, Query()] = None,
    started_to: Annotated[datetime | None, Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 25,
    sort: Annotated[IncidentSortField, Query()] = IncidentSortField.STARTED_AT,
    order: Annotated[SortOrder, Query()] = SortOrder.DESC,
) -> IncidentListResponse:
    normalized_from = _as_utc(started_from)
    normalized_to = _as_utc(started_to)
    if (
        normalized_from is not None
        and normalized_to is not None
        and normalized_from > normalized_to
    ):
        raise AppError(
            status_code=422,
            title="Incident filter validation failed",
            detail="started_from cannot be after started_to.",
            code="INCIDENT_INVALID_PERIOD",
            problem_slug="incident-invalid-period",
        )

    result = IncidentService(SqlAlchemyIncidentRepository(session)).list_incidents(
        context.tenant_id,
        IncidentListQuery(
            status=status_filter,
            severity=severity,
            started_from=normalized_from,
            started_to=normalized_to,
            page=page,
            page_size=page_size,
            sort=sort,
            order=order,
        ),
    )
    return IncidentListResponse(
        items=[
            IncidentResponse.model_validate(item, from_attributes=True)
            for item in result.items
        ],
        page=result.page,
        page_size=result.page_size,
        total=result.total,
    )
