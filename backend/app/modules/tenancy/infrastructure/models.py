from datetime import datetime, time
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Time,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TenantModel(Base):
    __tablename__ = "tenants"
    __table_args__ = (
        CheckConstraint(
            "char_length(slug) BETWEEN 2 AND 64",
            name="ck_tenants_slug_length",
        ),
        CheckConstraint(
            "char_length(name) BETWEEN 2 AND 120",
            name="ck_tenants_name_length",
        ),
        CheckConstraint("updated_at >= created_at", name="ck_tenants_updated_at"),
        CheckConstraint(
            "shift_duration_minutes BETWEEN 60 AND 1440 "
            "AND MOD(1440, shift_duration_minutes) = 0",
            name="ck_tenants_shift_duration",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    slug: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    timezone: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="UTC",
        server_default="UTC",
    )
    shift_start_local: Mapped[time] = mapped_column(
        Time,
        nullable=False,
        default=lambda: time(6, 0),
    )
    shift_duration_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=720,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
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


class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "char_length(external_subject) BETWEEN 1 AND 255",
            name="ck_users_external_subject_length",
        ),
        CheckConstraint("updated_at >= created_at", name="ck_users_updated_at"),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    external_subject: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
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


class TenantMembershipModel(Base):
    __tablename__ = "tenant_memberships"
    __table_args__ = (
        CheckConstraint(
            "role IN ('Admin','Supervisor','Operator','Viewer')",
            name="ck_tenant_memberships_role",
        ),
        CheckConstraint("updated_at >= created_at", name="ck_tenant_memberships_updated_at"),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role: Mapped[str] = mapped_column(String(24), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
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


Index("idx_tenant_memberships_user_id", TenantMembershipModel.user_id)
