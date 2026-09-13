from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class IncidentModel(Base):
    __tablename__ = "incidents"
    __table_args__ = (
        CheckConstraint(
            "char_length(title) BETWEEN 3 AND 120",
            name="ck_incidents_title_length",
        ),
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

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    affected_resource: Mapped[str] = mapped_column(String(120), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    impact_type: Mapped[str] = mapped_column(String(16), nullable=False)
    symptoms: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(24),
        nullable=False,
        default="OPEN",
        server_default="OPEN",
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_by_subject: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )


class IncidentEventModel(Base):
    __tablename__ = "incident_events"
    __table_args__ = (
        CheckConstraint(
            "event_type IN ('INCIDENT_CREATED','INCIDENT_UPDATED','INCIDENT_NORMALIZED')",
            name="ck_incident_events_type",
        ),
        CheckConstraint(
            "message IS NULL OR char_length(message) BETWEEN 3 AND 2000",
            name="ck_incident_events_message_length",
        ),
        CheckConstraint(
            "char_length(actor_subject) BETWEEN 1 AND 255",
            name="ck_incident_events_actor_subject_length",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "incident_id"],
            ["incidents.tenant_id", "incidents.id"],
            ondelete="RESTRICT",
            name="fk_incident_events_tenant_incident",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    incident_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    actor_subject: Mapped[str] = mapped_column(String(255), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


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
Index(
    "idx_incident_events_tenant_incident_occurred_at",
    IncidentEventModel.tenant_id,
    IncidentEventModel.incident_id,
    IncidentEventModel.occurred_at.asc(),
    IncidentEventModel.id.asc(),
)
