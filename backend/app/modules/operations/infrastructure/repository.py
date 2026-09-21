from datetime import time
from uuid import UUID, uuid4

from sqlalchemy import case, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.audit.infrastructure.repository import add_audit_event
from app.modules.incidents.domain.entities import IncidentSeverity, IncidentStatus
from app.modules.incidents.infrastructure.models import IncidentEventModel, IncidentModel
from app.modules.operations.application.services import HandoverVersionConflictError
from app.modules.operations.domain.entities import (
    DashboardItem,
    Handover,
    HandoverItem,
    HandoverListItem,
    HandoverPage,
    ShiftWindow,
)
from app.modules.operations.infrastructure.models import HandoverItemModel, HandoverModel
from app.modules.tenancy.infrastructure.models import TenantModel


class SqlAlchemyOperationsRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_shift_configuration(self, tenant_id: UUID) -> tuple[str, time, int]:
        tenant = self.session.get(TenantModel, tenant_id)
        if tenant is None or not tenant.is_active:
            raise LookupError("Active tenant not found.")
        return tenant.timezone, tenant.shift_start_local, tenant.shift_duration_minutes

    def list_dashboard_items(self, tenant_id: UUID) -> list[DashboardItem]:
        severity_rank = case(
            (IncidentModel.severity == "CRITICAL", 0),
            (IncidentModel.severity == "HIGH", 1),
            (IncidentModel.severity == "MEDIUM", 2),
            else_=3,
        )
        statement = (
            select(IncidentModel)
            .where(
                IncidentModel.tenant_id == tenant_id,
                IncidentModel.status.notin_(["RESOLVED", "CLOSED"]),
            )
            .order_by(severity_rank.asc(), IncidentModel.started_at.asc())
        )
        return [
            DashboardItem(
                id=model.id,
                title=model.title,
                affected_resource=model.affected_resource,
                severity=IncidentSeverity(model.severity),
                status=IncidentStatus(model.status),
                started_at=model.started_at,
                updated_at=model.updated_at,
            )
            for model in self.session.scalars(statement).all()
        ]

    def count_resolved_in_window(self, tenant_id: UUID, window: ShiftWindow) -> int:
        statement = (
            select(func.count(func.distinct(IncidentEventModel.incident_id)))
            .where(
                IncidentEventModel.tenant_id == tenant_id,
                IncidentEventModel.event_type == "INCIDENT_NORMALIZED",
                IncidentEventModel.occurred_at >= window.window_start,
                IncidentEventModel.occurred_at < window.window_end,
            )
        )
        return self.session.scalar(statement) or 0

    def _latest_event(self, tenant_id: UUID, incident_id: UUID):
        statement = (
            select(IncidentEventModel)
            .where(
                IncidentEventModel.tenant_id == tenant_id,
                IncidentEventModel.incident_id == incident_id,
            )
            .order_by(IncidentEventModel.occurred_at.desc(), IncidentEventModel.id.desc())
            .limit(1)
        )
        return self.session.scalar(statement)

    def list_handover_items(self, tenant_id: UUID, window: ShiftWindow) -> list[HandoverItem]:
        normalized_ids = (
            select(IncidentEventModel.incident_id)
            .where(
                IncidentEventModel.tenant_id == tenant_id,
                IncidentEventModel.event_type == "INCIDENT_NORMALIZED",
                IncidentEventModel.occurred_at >= window.window_start,
                IncidentEventModel.occurred_at < window.window_end,
            )
            .distinct()
        )
        severity_rank = case(
            (IncidentModel.severity == "CRITICAL", 0),
            (IncidentModel.severity == "HIGH", 1),
            (IncidentModel.severity == "MEDIUM", 2),
            else_=3,
        )
        statement = (
            select(IncidentModel)
            .where(
                IncidentModel.tenant_id == tenant_id,
                or_(
                    IncidentModel.status.notin_(["RESOLVED", "CLOSED"]),
                    IncidentModel.id.in_(normalized_ids),
                ),
            )
            .order_by(severity_rank.asc(), IncidentModel.started_at.asc())
        )
        result: list[HandoverItem] = []
        for incident in self.session.scalars(statement).all():
            event = self._latest_event(tenant_id, incident.id)
            result.append(
                HandoverItem(
                    incident_id=incident.id,
                    title=incident.title,
                    affected_resource=incident.affected_resource,
                    severity=IncidentSeverity(incident.severity),
                    status=IncidentStatus(incident.status),
                    started_at=incident.started_at,
                    last_event_message=event.message if event else None,
                    last_event_at=event.occurred_at if event else None,
                )
            )
        return result

    def create_handover(
        self,
        tenant_id: UUID,
        actor_subject: str,
        window: ShiftWindow,
        observations: str | None,
        items: list[HandoverItem],
    ) -> Handover:
        latest_version = self.session.scalar(
            select(func.max(HandoverModel.version)).where(
                HandoverModel.tenant_id == tenant_id,
                HandoverModel.window_start == window.window_start,
                HandoverModel.window_end == window.window_end,
            )
        )
        version = (latest_version or 0) + 1
        finalized_at = func.now()
        model = HandoverModel(
            id=uuid4(),
            tenant_id=tenant_id,
            window_start=window.window_start,
            window_end=window.window_end,
            version=version,
            observations=observations,
            finalized_by_subject=actor_subject,
            finalized_at=finalized_at,
        )
        try:
            self.session.add(model)
            self.session.flush()
            for item in items:
                self.session.add(
                    HandoverItemModel(
                        id=uuid4(),
                        handover_id=model.id,
                        incident_id=item.incident_id,
                        title_snapshot=item.title,
                        affected_resource_snapshot=item.affected_resource,
                        severity_snapshot=item.severity.value,
                        status_snapshot=item.status.value,
                        started_at_snapshot=item.started_at,
                        last_event_message_snapshot=item.last_event_message,
                        last_event_at_snapshot=item.last_event_at,
                    )
                )
            add_audit_event(
                self.session,
                tenant_id=tenant_id,
                actor_subject=actor_subject,
                action="handover.finalized",
                resource_type="handover",
                resource_id=model.id,
            )
            self.session.commit()
            self.session.refresh(model)
        except IntegrityError as exc:
            self.session.rollback()
            raise HandoverVersionConflictError from exc
        return self._to_handover(model)

    def _items_for(self, handover_id: UUID) -> list[HandoverItem]:
        statement = (
            select(HandoverItemModel)
            .where(HandoverItemModel.handover_id == handover_id)
            .order_by(HandoverItemModel.started_at_snapshot.asc(), HandoverItemModel.id.asc())
        )
        return [
            HandoverItem(
                incident_id=item.incident_id,
                title=item.title_snapshot,
                affected_resource=item.affected_resource_snapshot,
                severity=IncidentSeverity(item.severity_snapshot),
                status=IncidentStatus(item.status_snapshot),
                started_at=item.started_at_snapshot,
                last_event_message=item.last_event_message_snapshot,
                last_event_at=item.last_event_at_snapshot,
            )
            for item in self.session.scalars(statement).all()
        ]

    def _to_handover(self, model: HandoverModel) -> Handover:
        return Handover(
            id=model.id,
            version=model.version,
            window_start=model.window_start,
            window_end=model.window_end,
            observations=model.observations,
            finalized_by_subject=model.finalized_by_subject,
            finalized_at=model.finalized_at,
            items=self._items_for(model.id),
        )

    def list_handovers(self, tenant_id: UUID, page: int, page_size: int) -> HandoverPage:
        total = self.session.scalar(
            select(func.count()).select_from(HandoverModel).where(
                HandoverModel.tenant_id == tenant_id
            )
        ) or 0
        statement = (
            select(HandoverModel)
            .where(HandoverModel.tenant_id == tenant_id)
            .order_by(HandoverModel.finalized_at.desc(), HandoverModel.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = [
            HandoverListItem(
                id=model.id,
                version=model.version,
                window_start=model.window_start,
                window_end=model.window_end,
                finalized_by_subject=model.finalized_by_subject,
                finalized_at=model.finalized_at,
            )
            for model in self.session.scalars(statement).all()
        ]
        return HandoverPage(items=items, page=page, page_size=page_size, total=total)

    def get_latest_handover(self, tenant_id: UUID) -> Handover | None:
        model = self.session.scalar(
            select(HandoverModel)
            .where(HandoverModel.tenant_id == tenant_id)
            .order_by(HandoverModel.finalized_at.desc(), HandoverModel.id.desc())
            .limit(1)
        )
        return self._to_handover(model) if model else None

    def get_handover(self, tenant_id: UUID, handover_id: UUID) -> Handover | None:
        model = self.session.scalar(
            select(HandoverModel).where(
                HandoverModel.tenant_id == tenant_id,
                HandoverModel.id == handover_id,
            )
        )
        return self._to_handover(model) if model else None
