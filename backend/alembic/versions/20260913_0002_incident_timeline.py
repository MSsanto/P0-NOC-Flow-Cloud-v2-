"""Add append-only incident timeline for Sprint 2.

Revision ID: 20260913_0002
Revises: 20260908_0001
Create Date: 2026-09-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260913_0002"
down_revision: str | None = "20260908_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "incident_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("incident_id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(length=32), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("actor_subject", sa.String(length=255), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "event_type IN "
            "('INCIDENT_CREATED','INCIDENT_UPDATED','INCIDENT_NORMALIZED')",
            name="ck_incident_events_type",
        ),
        sa.CheckConstraint(
            "message IS NULL OR char_length(message) BETWEEN 3 AND 2000",
            name="ck_incident_events_message_length",
        ),
        sa.CheckConstraint(
            "char_length(actor_subject) BETWEEN 1 AND 255",
            name="ck_incident_events_actor_subject_length",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "incident_id"],
            ["incidents.tenant_id", "incidents.id"],
            name="fk_incident_events_tenant_incident",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_incident_events_tenant_incident_occurred_at",
        "incident_events",
        ["tenant_id", "incident_id", "occurred_at", "id"],
        unique=False,
    )

    op.execute(
        sa.text(
            """
            INSERT INTO incident_events (
                id,
                tenant_id,
                incident_id,
                event_type,
                message,
                actor_subject,
                occurred_at
            )
            SELECT
                id,
                tenant_id,
                id,
                'INCIDENT_CREATED',
                NULL,
                created_by_subject,
                created_at
            FROM incidents
            """
        )
    )


def downgrade() -> None:
    op.drop_index(
        "idx_incident_events_tenant_incident_occurred_at",
        table_name="incident_events",
    )
    op.drop_table("incident_events")
