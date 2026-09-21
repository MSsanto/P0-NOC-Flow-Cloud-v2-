from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AuditEventModel(Base):
    __tablename__ = "audit_events"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )
    actor_subject: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    request_id: Mapped[str] = mapped_column(String(128), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


Index(
    "idx_audit_events_tenant_occurred_at",
    AuditEventModel.tenant_id,
    AuditEventModel.occurred_at.desc(),
)
Index(
    "idx_audit_events_tenant_action_occurred_at",
    AuditEventModel.tenant_id,
    AuditEventModel.action,
    AuditEventModel.occurred_at.desc(),
)
Index(
    "idx_audit_events_tenant_resource",
    AuditEventModel.tenant_id,
    AuditEventModel.resource_type,
    AuditEventModel.resource_id,
)
