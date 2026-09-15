from uuid import uuid4

import pytest
from sqlalchemy import delete, select

from app.core.config import Settings
from app.core.errors import AppError
from app.db.session import get_session_factory
from app.modules.tenancy.application.security import Role
from app.modules.tenancy.infrastructure.cloudflare_access_provider import (
    CloudflareAccessIdentity,
)
from app.modules.tenancy.infrastructure.models import (
    TenantMembershipModel,
    TenantModel,
    UserModel,
)
from app.modules.tenancy.presentation import dependencies


@pytest.fixture(autouse=True)
def clean_identity_tables():
    factory = get_session_factory()
    with factory() as session:
        session.execute(delete(TenantMembershipModel))
        session.execute(delete(UserModel))
        session.execute(delete(TenantModel))
        session.commit()
    yield
    with factory() as session:
        session.execute(delete(TenantMembershipModel))
        session.execute(delete(UserModel))
        session.execute(delete(TenantModel))
        session.commit()


def _settings(tenant_id, *, bootstrap_email: str | None) -> Settings:
    return Settings(
        environment="staging",
        auth_mode="cloudflare_access",
        cloudflare_access_team_domain="https://nocflow.cloudflareaccess.com",
        cloudflare_access_audience="test-audience",
        cloudflare_access_tenant_id=tenant_id,
        cloudflare_access_bootstrap_admin_email=bootstrap_email,
    )


def _install_identity(monkeypatch, *, subject: str, email: str) -> None:
    class FakeValidator:
        def __init__(self, _settings: Settings) -> None:
            pass

        def validate(self, _token: str) -> CloudflareAccessIdentity:
            return CloudflareAccessIdentity(subject=subject, email=email)

    monkeypatch.setattr(dependencies, "CloudflareAccessTokenValidator", FakeValidator)


def test_configured_cloudflare_bootstrap_email_creates_first_admin(monkeypatch) -> None:
    tenant_id = uuid4()
    _install_identity(
        monkeypatch,
        subject="cf-user-123",
        email="admin@example.test",
    )

    factory = get_session_factory()
    with factory() as session:
        session.add(
            TenantModel(
                id=tenant_id,
                slug="tenant-a",
                name="Tenant A",
                timezone="UTC",
                is_active=True,
            )
        )
        session.commit()

        context = dependencies.get_request_context(
            credentials=None,
            session=session,
            settings=_settings(tenant_id, bootstrap_email="admin@example.test"),
            cloudflare_access_token="signed-access-token",
        )

        user = session.scalar(
            select(UserModel).where(UserModel.external_subject == "cf-user-123")
        )
        assert user is not None
        membership = session.get(TenantMembershipModel, (tenant_id, user.id))

    assert context.actor_subject == "admin@example.test"
    assert context.roles == frozenset({Role.ADMIN})
    assert membership is not None
    assert membership.role == Role.ADMIN.value


def test_unconfigured_cloudflare_identity_does_not_self_provision(monkeypatch) -> None:
    tenant_id = uuid4()
    _install_identity(
        monkeypatch,
        subject="cf-user-999",
        email="intruder@example.test",
    )

    factory = get_session_factory()
    with factory() as session:
        session.add(
            TenantModel(
                id=tenant_id,
                slug="tenant-a",
                name="Tenant A",
                timezone="UTC",
                is_active=True,
            )
        )
        session.commit()

        with pytest.raises(AppError) as exc_info:
            dependencies.get_request_context(
                credentials=None,
                session=session,
                settings=_settings(tenant_id, bootstrap_email="admin@example.test"),
                cloudflare_access_token="signed-access-token",
            )

    assert exc_info.value.status_code == 403
    assert exc_info.value.code == "TENANT_ACCESS_DENIED"
