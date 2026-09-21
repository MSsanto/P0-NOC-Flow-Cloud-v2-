"""Add append-only audit events for Sprint 5.

Revision ID: 20260921_0005
Revises: 20260921_0004
Create Date: 2026-09-21
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260921_0005"
down_revision: str | None = "20260921_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("actor_subject", sa.String(length=255), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("resource_type", sa.String(length=64), nullable=False),
        sa.Column("resource_id", sa.Uuid(), nullable=True),
        sa.Column("request_id", sa.String(length=128), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_audit_events_tenant_occurred_at",
        "audit_events",
        ["tenant_id", "occurred_at"],
        unique=False,
    )
    op.create_index(
        "idx_audit_events_tenant_action_occurred_at",
        "audit_events",
        ["tenant_id", "action", "occurred_at"],
        unique=False,
    )
    op.create_index(
        "idx_audit_events_tenant_resource",
        "audit_events",
        ["tenant_id", "resource_type", "resource_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_audit_events_tenant_resource", table_name="audit_events")
    op.drop_index("idx_audit_events_tenant_action_occurred_at", table_name="audit_events")
    op.drop_index("idx_audit_events_tenant_occurred_at", table_name="audit_events")
    op.drop_table("audit_events")
