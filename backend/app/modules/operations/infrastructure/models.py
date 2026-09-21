from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
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


class HandoverModel(Base):
    __tablename__ = "handovers"
    __table_args__ = (
        CheckConstraint("version >= 1", name="ck_handovers_version"),
        CheckConstraint("window_end > window_start", name="ck_handovers_window"),
        CheckConstraint(
            "observations IS NULL OR char_length(observations) BETWEEN 3 AND 4000",
            name="ck_handovers_observations_length",
        ),
        CheckConstraint(
            "char_length(finalized_by_subject) BETWEEN 1 AND 255",
            name="ck_handovers_finalized_by_subject_length",
        ),
        UniqueConstraint(
            "tenant_id",
            "window_start",
            "window_end",
            "version",
            name="uq_handovers_tenant_window_version",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    observations: Mapped[str | None] = mapped_column(Text, nullable=True)
    finalized_by_subject: Mapped[str] = mapped_column(String(255), nullable=False)
    finalized_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class HandoverItemModel(Base):
    __tablename__ = "handover_items"
    __table_args__ = (
        UniqueConstraint(
            "handover_id",
            "incident_id",
            name="uq_handover_items_handover_incident",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    handover_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("handovers.id", ondelete="CASCADE"),
        nullable=False,
    )
    incident_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("incidents.id", ondelete="RESTRICT"),
        nullable=False,
    )
    title_snapshot: Mapped[str] = mapped_column(String(120), nullable=False)
    affected_resource_snapshot: Mapped[str] = mapped_column(String(120), nullable=False)
    severity_snapshot: Mapped[str] = mapped_column(String(16), nullable=False)
    status_snapshot: Mapped[str] = mapped_column(String(24), nullable=False)
    started_at_snapshot: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_event_message_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_event_at_snapshot: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


Index(
    "idx_handovers_tenant_finalized_at",
    HandoverModel.tenant_id,
    HandoverModel.finalized_at.desc(),
)
Index(
    "idx_handovers_tenant_window_version",
    HandoverModel.tenant_id,
    HandoverModel.window_start.desc(),
    HandoverModel.version.desc(),
)
Index("idx_handover_items_handover_id", HandoverItemModel.handover_id)
