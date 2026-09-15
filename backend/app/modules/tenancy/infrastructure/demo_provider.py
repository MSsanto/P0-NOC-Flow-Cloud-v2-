from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.modules.tenancy.application.context import RequestContext
from app.modules.tenancy.application.security import Role
from app.modules.tenancy.infrastructure.models import (
    TenantMembershipModel,
    TenantModel,
    UserModel,
)


class DemoContextUnavailableError(RuntimeError):
    pass


def resolve_demo_context(session: Session, settings: Settings) -> RequestContext:
    if settings.environment not in {"development", "test"}:
        raise DemoContextUnavailableError(
            "Demo context is disabled outside development and test."
        )

    tenant = session.get(TenantModel, settings.demo_tenant_id)
    if tenant is None:
        tenant = TenantModel(
            id=settings.demo_tenant_id,
            slug="demo",
            name="NOC Flow Demo Tenant",
            timezone="UTC",
            is_active=True,
        )
        session.add(tenant)
        session.flush()
    elif not tenant.is_active:
        raise DemoContextUnavailableError("Demo tenant is inactive.")

    user = session.scalar(
        select(UserModel).where(UserModel.external_subject == settings.demo_actor_subject)
    )
    if user is None:
        user = UserModel(external_subject=settings.demo_actor_subject, is_active=True)
        session.add(user)
        session.flush()
    elif not user.is_active:
        raise DemoContextUnavailableError("Demo user is inactive.")

    membership = session.get(
        TenantMembershipModel,
        (settings.demo_tenant_id, user.id),
    )
    if membership is None:
        membership = TenantMembershipModel(
            tenant_id=settings.demo_tenant_id,
            user_id=user.id,
            role=Role.ADMIN.value,
            is_active=True,
        )
        session.add(membership)
    elif not membership.is_active:
        raise DemoContextUnavailableError("Demo membership is inactive.")

    session.commit()

    return RequestContext(
        tenant_id=settings.demo_tenant_id,
        actor_subject=settings.demo_actor_subject,
        roles=frozenset({Role(membership.role)}),
    )
