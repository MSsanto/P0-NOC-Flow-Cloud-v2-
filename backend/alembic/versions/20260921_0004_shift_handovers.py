"""Add shift configuration and handover snapshot tables for Sprint 4.

Revision ID: 20260921_0004
Revises: 20260915_0003
Create Date: 2026-09-21
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260921_0004"
down_revision: str | None = "20260915_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("tenants", sa.Column("shift_start_local", sa.Time(), nullable=True))
    op.add_column(
        "tenants",
        sa.Column("shift_duration_minutes", sa.Integer(), nullable=True),
    )
    op.execute("UPDATE tenants SET shift_start_local = '06:00:00' WHERE shift_start_local IS NULL")
    op.execute(
        "UPDATE tenants SET shift_duration_minutes = 720 "
        "WHERE shift_duration_minutes IS NULL"
    )
    op.alter_column("tenants", "shift_start_local", nullable=False)
    op.alter_column("tenants", "shift_duration_minutes", nullable=False)
    op.create_check_constraint(
        "ck_tenants_shift_duration",
        "tenants",
        "shift_duration_minutes BETWEEN 60 AND 1440 "
        "AND MOD(1440, shift_duration_minutes) = 0",
    )

    op.create_table(
        "handovers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("observations", sa.Text(), nullable=True),
        sa.Column("finalized_by_subject", sa.String(length=255), nullable=False),
        sa.Column("finalized_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("version >= 1", name="ck_handovers_version"),
        sa.CheckConstraint("window_end > window_start", name="ck_handovers_window"),
        sa.CheckConstraint(
            "observations IS NULL OR char_length(observations) BETWEEN 3 AND 4000",
            name="ck_handovers_observations_length",
        ),
        sa.CheckConstraint(
            "char_length(finalized_by_subject) BETWEEN 1 AND 255",
            name="ck_handovers_finalized_by_subject_length",
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "window_start",
            "window_end",
            "version",
            name="uq_handovers_tenant_window_version",
        ),
    )
    op.create_index(
        "idx_handovers_tenant_finalized_at",
        "handovers",
        ["tenant_id", "finalized_at"],
        unique=False,
    )
    op.create_index(
        "idx_handovers_tenant_window_version",
        "handovers",
        ["tenant_id", "window_start", "version"],
        unique=False,
    )

    op.create_table(
        "handover_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("handover_id", sa.Uuid(), nullable=False),
        sa.Column("incident_id", sa.Uuid(), nullable=False),
        sa.Column("title_snapshot", sa.String(length=120), nullable=False),
        sa.Column("affected_resource_snapshot", sa.String(length=120), nullable=False),
        sa.Column("severity_snapshot", sa.String(length=16), nullable=False),
        sa.Column("status_snapshot", sa.String(length=24), nullable=False),
        sa.Column("started_at_snapshot", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_event_message_snapshot", sa.Text(), nullable=True),
        sa.Column("last_event_at_snapshot", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["handover_id"],
            ["handovers.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["incident_id"],
            ["incidents.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "handover_id",
            "incident_id",
            name="uq_handover_items_handover_incident",
        ),
    )
    op.create_index(
        "idx_handover_items_handover_id",
        "handover_items",
        ["handover_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_handover_items_handover_id", table_name="handover_items")
    op.drop_table("handover_items")
    op.drop_index("idx_handovers_tenant_window_version", table_name="handovers")
    op.drop_index("idx_handovers_tenant_finalized_at", table_name="handovers")
    op.drop_table("handovers")
    op.drop_constraint("ck_tenants_shift_duration", "tenants", type_="check")
    op.drop_column("tenants", "shift_duration_minutes")
    op.drop_column("tenants", "shift_start_local")
