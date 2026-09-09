from sqlalchemy.orm import Session

from app.core.config import Settings
from app.modules.tenancy.application.context import RequestContext
from app.modules.tenancy.infrastructure.models import TenantModel


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
        session.commit()

    return RequestContext(
        tenant_id=settings.demo_tenant_id,
        actor_subject=settings.demo_actor_subject,
    )
