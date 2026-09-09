from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.incidents.domain.entities import (
    Incident,
    IncidentImpactType,
    IncidentSeverity,
    IncidentStatus,
)
from app.modules.incidents.infrastructure.models import IncidentModel


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


class SqlAlchemyIncidentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_for_tenant(self, tenant_id: UUID) -> list[Incident]:
        statement = (
            select(IncidentModel)
            .where(IncidentModel.tenant_id == tenant_id)
            .order_by(IncidentModel.started_at.desc(), IncidentModel.created_at.desc())
        )
        return [_to_domain(model) for model in self.session.scalars(statement).all()]

    def get_for_tenant(self, tenant_id: UUID, incident_id: UUID) -> Incident | None:
        statement = select(IncidentModel).where(
            IncidentModel.tenant_id == tenant_id,
            IncidentModel.id == incident_id,
        )
        model = self.session.scalar(statement)
        return _to_domain(model) if model is not None else None

    def create(self, incident: Incident) -> Incident:
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
        self.session.commit()
        self.session.refresh(model)
        return _to_domain(model)
