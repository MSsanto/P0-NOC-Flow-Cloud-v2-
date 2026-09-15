from uuid import UUID, uuid4

import pytest
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import delete

from app.core.config import Settings
from app.core.errors import AppError
from app.db.session import get_session_factory
from app.modules.tenancy.application.security import Role
from app.modules.tenancy.infrastructure.models import (
    TenantMembershipModel,
    TenantModel,
    UserModel,
)
from app.modules.tenancy.infrastructure.oidc_provider import ExternalIdentity
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


def _settings() -> Settings:
    return Settings(
        environment="test",
        auth_mode="oidc",
        oidc_issuer="https://identity.example.test/",
        oidc_audience="noc-flow-api",
        oidc_jwks_url="https://identity.example.test/jwks.json",
    )


def _credentials() -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials="signed-token")


def _install_identity(monkeypatch, *, subject: str, tenant_id: UUID) -> None:
    class FakeValidator:
        def __init__(self, _settings: Settings) -> None:
            pass

        def validate(self, _token: str) -> ExternalIdentity:
            return ExternalIdentity(subject=subject, requested_tenant_id=tenant_id)

    monkeypatch.setattr(dependencies, "OidcTokenValidator", FakeValidator)


def test_oidc_context_uses_internal_membership_role(monkeypatch) -> None:
    tenant_id = uuid4()
    user_id = uuid4()
    _install_identity(
        monkeypatch,
        subject="operator@example.test",
        tenant_id=tenant_id,
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
        session.add(
            UserModel(
                id=user_id,
                external_subject="operator@example.test",
                is_active=True,
            )
        )
        session.add(
            TenantMembershipModel(
                tenant_id=tenant_id,
                user_id=user_id,
                role=Role.VIEWER.value,
                is_active=True,
            )
        )
        session.commit()

        context = dependencies.get_request_context(
            credentials=_credentials(),
            session=session,
            settings=_settings(),
        )

    assert context.tenant_id == tenant_id
    assert context.actor_subject == "operator@example.test"
    assert context.roles == frozenset({Role.VIEWER})


def test_cross_tenant_request_without_membership_is_denied(monkeypatch) -> None:
    tenant_a = uuid4()
    tenant_b = uuid4()
    user_id = uuid4()
    _install_identity(
        monkeypatch,
        subject="operator@example.test",
        tenant_id=tenant_b,
    )

    factory = get_session_factory()
    with factory() as session:
        session.add_all(
            [
                TenantModel(
                    id=tenant_a,
                    slug="tenant-a",
                    name="Tenant A",
                    timezone="UTC",
                    is_active=True,
                ),
                TenantModel(
                    id=tenant_b,
                    slug="tenant-b",
                    name="Tenant B",
                    timezone="UTC",
                    is_active=True,
                ),
                UserModel(
                    id=user_id,
                    external_subject="operator@example.test",
                    is_active=True,
                ),
                TenantMembershipModel(
                    tenant_id=tenant_a,
                    user_id=user_id,
                    role=Role.OPERATOR.value,
                    is_active=True,
                ),
            ]
        )
        session.commit()

        with pytest.raises(AppError) as exc_info:
            dependencies.get_request_context(
                credentials=_credentials(),
                session=session,
                settings=_settings(),
            )

    assert exc_info.value.status_code == 403
    assert exc_info.value.code == "TENANT_ACCESS_DENIED"


def test_inactive_membership_is_denied(monkeypatch) -> None:
    tenant_id = uuid4()
    user_id = uuid4()
    _install_identity(
        monkeypatch,
        subject="operator@example.test",
        tenant_id=tenant_id,
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
        session.add(
            UserModel(
                id=user_id,
                external_subject="operator@example.test",
                is_active=True,
            )
        )
        session.add(
            TenantMembershipModel(
                tenant_id=tenant_id,
                user_id=user_id,
                role=Role.OPERATOR.value,
                is_active=False,
            )
        )
        session.commit()

        with pytest.raises(AppError) as exc_info:
            dependencies.get_request_context(
                credentials=_credentials(),
                session=session,
                settings=_settings(),
            )

    assert exc_info.value.status_code == 403
    assert exc_info.value.code == "TENANT_ACCESS_DENIED"
