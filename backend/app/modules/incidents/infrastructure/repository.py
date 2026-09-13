from uuid import UUID

from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import Session

from app.modules.incidents.application.queries import (
    IncidentListQuery,
    IncidentPage,
    IncidentSortField,
    SortOrder,
)
from app.modules.incidents.domain.entities import (
    Incident,
    IncidentEvent,
    IncidentEventType,
    IncidentImpactType,
    IncidentSeverity,
    IncidentStatus,
)
from app.modules.incidents.infrastructure.models import IncidentEventModel, IncidentModel


def _to_domain(model: IncidentModel) -> Incident:
    return Incident(
        id=model.id,
        tenant_id=model.tenant_id,
        title=model.title,
        affected_resource=model.affected_resource,
        severity=IncidentSeverity(model.severity),
        impact_type=IncidentImpactType(model.impact_type),
        symptoms=model.symptoms,
        status=IncidentStatus(model.status),
        started_at=model.started_at,
        created_by_subject=model.created_by_subject,
        created_at=model.created_at,
        updated_at=model.updated_at,
        version=model.version,
    )


def _to_event_domain(model: IncidentEventModel) -> IncidentEvent:
    return IncidentEvent(
        id=model.id,
        tenant_id=model.tenant_id,
        incident_id=model.incident_id,
        event_type=IncidentEventType(model.event_type),
        message=model.message,
        actor_subject=model.actor_subject,
        occurred_at=model.occurred_at,
    )


def _event_model(event: IncidentEvent) -> IncidentEventModel:
    return IncidentEventModel(
        id=event.id,
        tenant_id=event.tenant_id,
        incident_id=event.incident_id,
        event_type=event.event_type.value,
        message=event.message,
        actor_subject=event.actor_subject,
        occurred_at=event.occurred_at,
    )


class SqlAlchemyIncidentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_for_tenant(self, tenant_id: UUID, query: IncidentListQuery) -> IncidentPage:
        conditions = [IncidentModel.tenant_id == tenant_id]
        if query.status is not None:
            conditions.append(IncidentModel.status == query.status.value)
        if query.severity is not None:
            conditions.append(IncidentModel.severity == query.severity.value)
        if query.started_from is not None:
            conditions.append(IncidentModel.started_at >= query.started_from)
        if query.started_to is not None:
            conditions.append(IncidentModel.started_at <= query.started_to)

        total_statement = select(func.count()).select_from(IncidentModel).where(*conditions)
        total = self.session.scalar(total_statement) or 0

        sort_column = (
            IncidentModel.updated_at
            if query.sort is IncidentSortField.UPDATED_AT
            else IncidentModel.started_at
        )
        direction = asc if query.order is SortOrder.ASC else desc
        statement = (
            select(IncidentModel)
            .where(*conditions)
            .order_by(direction(sort_column), direction(IncidentModel.created_at))
            .offset(query.offset)
            .limit(query.page_size)
        )
        items = [_to_domain(model) for model in self.session.scalars(statement).all()]
        return IncidentPage(
            items=items,
            page=query.page,
            page_size=query.page_size,
            total=total,
        )

    def get_for_tenant(self, tenant_id: UUID, incident_id: UUID) -> Incident | None:
        statement = select(IncidentModel).where(
            IncidentModel.tenant_id == tenant_id,
            IncidentModel.id == incident_id,
        )
        model = self.session.scalar(statement)
        return _to_domain(model) if model is not None else None

    def create(self, incident: Incident, event: IncidentEvent) -> Incident:
        model = IncidentModel(
            id=incident.id,
            tenant_id=incident.tenant_id,
            title=incident.title,
            affected_resource=incident.affected_resource,
            severity=incident.severity.value,
            impact_type=incident.impact_type.value,
            symptoms=incident.symptoms,
            status=incident.status.value,
            started_at=incident.started_at,
            created_by_subject=incident.created_by_subject,
            created_at=incident.created_at,
            updated_at=incident.updated_at,
            version=incident.version,
        )
        self.session.add(model)
        self.session.flush()
        self.session.add(_event_model(event))
        self.session.commit()
        self.session.refresh(model)
        return _to_domain(model)

    def save_with_event(self, incident: Incident, event: IncidentEvent) -> Incident:
        statement = select(IncidentModel).where(
            IncidentModel.tenant_id == incident.tenant_id,
            IncidentModel.id == incident.id,
        )
        model = self.session.scalar(statement)
        if model is None:
            raise LookupError("Incident no longer exists in the active tenant.")

        model.status = incident.status.value
        model.updated_at = incident.updated_at
        model.version = incident.version
        self.session.add(_event_model(event))
        self.session.commit()
        self.session.refresh(model)
        return _to_domain(model)

    def list_events_for_incident(
        self,
        tenant_id: UUID,
        incident_id: UUID,
    ) -> list[IncidentEvent]:
        statement = (
            select(IncidentEventModel)
            .where(
                IncidentEventModel.tenant_id == tenant_id,
                IncidentEventModel.incident_id == incident_id,
            )
            .order_by(IncidentEventModel.occurred_at.asc(), IncidentEventModel.id.asc())
        )
        return [
            _to_event_domain(model) for model in self.session.scalars(statement).all()
        ]
