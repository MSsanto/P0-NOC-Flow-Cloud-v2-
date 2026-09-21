from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.request_context import current_request_id
from app.modules.audit.infrastructure.models import AuditEventModel


def add_audit_event(
    session: Session,
    *,
    tenant_id: UUID,
    actor_subject: str,
    action: str,
    resource_type: str,
    resource_id: UUID | None,
) -> None:
    session.add(
        AuditEventModel(
            id=uuid4(),
            tenant_id=tenant_id,
            actor_subject=actor_subject,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            request_id=current_request_id(),
            occurred_at=datetime.now(UTC),
        )
    )


class SqlAlchemyAuditRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_for_tenant(
        self,
        tenant_id: UUID,
        *,
        page: int,
        page_size: int,
        action: str | None = None,
        resource_type: str | None = None,
    ) -> tuple[list[AuditEventModel], int]:
        conditions = [AuditEventModel.tenant_id == tenant_id]
        if action:
            conditions.append(AuditEventModel.action == action)
        if resource_type:
            conditions.append(AuditEventModel.resource_type == resource_type)

        total = self.session.scalar(
            select(func.count()).select_from(AuditEventModel).where(*conditions)
        ) or 0
        statement = (
            select(AuditEventModel)
            .where(*conditions)
            .order_by(AuditEventModel.occurred_at.desc(), AuditEventModel.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(self.session.scalars(statement).all()), total
