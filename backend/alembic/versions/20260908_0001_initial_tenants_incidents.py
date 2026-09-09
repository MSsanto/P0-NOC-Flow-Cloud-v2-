"""Create Sprint 1 tenants and incidents tables.

Revision ID: 20260908_0001
Revises:
Create Date: 2026-09-08
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260908_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("timezone", sa.String(length=64), server_default=sa.text("'UTC'"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "char_length(slug) BETWEEN 2 AND 64",
            name="ck_tenants_slug_length",
        ),
        sa.CheckConstraint(
            "char_length(name) BETWEEN 2 AND 120",
            name="ck_tenants_name_length",
        ),
        sa.CheckConstraint("updated_at >= created_at", name="ck_tenants_updated_at"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    op.create_table(
        "incidents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("affected_resource", sa.String(length=120), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("impact_type", sa.String(length=16), nullable=False),
        sa.Column("symptoms", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=24),
            server_default=sa.text("'OPEN'"),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by_subject", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.CheckConstraint(
            "char_length(title) BETWEEN 3 AND 120",
            name="ck_incidents_title_length",
        ),
        sa.CheckConstraint(
            "char_length(affected_resource) BETWEEN 2 AND 120",
            name="ck_incidents_affected_resource_length",
        ),
        sa.CheckConstraint(
            "severity IN ('CRITICAL','HIGH','MEDIUM','LOW')",
            name="ck_incidents_severity",
        ),
        sa.CheckConstraint(
            "impact_type IN ('OUTAGE','DEGRADATION')",
            name="ck_incidents_impact_type",
        ),
        sa.CheckConstraint(
            "char_length(symptoms) BETWEEN 10 AND 2000",
            name="ck_incidents_symptoms_length",
        ),
        sa.CheckConstraint(
            "status IN ('OPEN','ACKNOWLEDGED','INVESTIGATING','MONITORING','RESOLVED','CLOSED')",
            name="ck_incidents_status",
        ),
        sa.CheckConstraint("started_at <= created_at", name="ck_incidents_started_at"),
        sa.CheckConstraint("updated_at >= created_at", name="ck_incidents_updated_at"),
        sa.CheckConstraint("version >= 1", name="ck_incidents_version"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_incidents_tenant_id_id"),
    )

    op.create_index(
        "idx_incidents_tenant_started_at",
        "incidents",
        ["tenant_id", sa.text("started_at DESC"), sa.text("created_at DESC")],
        unique=False,
    )
    op.create_index(
        "idx_incidents_tenant_status_started_at",
        "incidents",
        ["tenant_id", "status", sa.text("started_at DESC")],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_incidents_tenant_status_started_at", table_name="incidents")
    op.drop_index("idx_incidents_tenant_started_at", table_name="incidents")
    op.drop_table("incidents")
    op.drop_table("tenants")
