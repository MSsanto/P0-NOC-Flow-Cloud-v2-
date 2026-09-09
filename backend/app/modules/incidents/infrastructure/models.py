from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class IncidentModel(Base):
    __tablename__ = "incidents"
    __table_args__ = (
        CheckConstraint("char_length(title) BETWEEN 3 AND 120", name="ck_incidents_title_length"),
        CheckConstraint(
            "char_length(affected_resource) BETWEEN 2 AND 120",
            name="ck_incidents_affected_resource_length",
        ),
        CheckConstraint(
            "severity IN ('CRITICAL','HIGH','MEDIUM','LOW')",
            name="ck_incidents_severity",
        ),
        CheckConstraint(
            "impact_type IN ('OUTAGE','DEGRADATION')",
            name="ck_incidents_impact_type",
        ),
        CheckConstraint(
            "char_length(symptoms) BETWEEN 10 AND 2000",
            name="ck_incidents_symptoms_length",
        ),
        CheckConstraint(
            "status IN ('OPEN','ACKNOWLEDGED','INVESTIGATING','MONITORING','RESOLVED','CLOSED')",
            name="ck_incidents_status",
        ),
        CheckConstraint("started_at <= created_at", name="ck_incidents_started_at"),
        CheckConstraint("updated_at >= created_at", name="ck_incidents_updated_at"),
        CheckConstraint("version >= 1", name="ck_incidents_version"),
        UniqueConstraint("tenant_id", "id", name="uq_incidents_tenant_id_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    affected_resource: Mapped[str] = mapped_column(String(120), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    impact_type: Mapped[str] = mapped_column(String(16), nullable=False)
    symptoms: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="OPEN", server_default="OPEN")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_by_subject: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")


Index(
    "idx_incidents_tenant_started_at",
    IncidentModel.tenant_id,
    IncidentModel.started_at.desc(),
    IncidentModel.created_at.desc(),
)
Index(
    "idx_incidents_tenant_status_started_at",
    IncidentModel.tenant_id,
    IncidentModel.status,
    IncidentModel.started_at.desc(),
)
