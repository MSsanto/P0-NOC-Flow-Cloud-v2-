from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import UUID

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from app.core.config import Settings
from app.core.errors import AppError
from app.modules.tenancy.application.context import RequestContext
from app.modules.tenancy.application.security import Permission, Role, permissions_for_roles
from app.modules.tenancy.infrastructure.oidc_provider import (
    AuthenticationError,
    IdentityProviderConfigurationError,
    OidcConfiguration,
    OidcTokenValidator,
)
from app.modules.tenancy.presentation.dependencies import get_request_context, require_permission


class FakeJwkClient:
    def __init__(self, public_key) -> None:
        self.public_key = public_key

    def get_signing_key_from_jwt(self, _token: str):
        return SimpleNamespace(key=self.public_key)


def _settings() -> Settings:
    return Settings(
        environment="test",
        auth_mode="oidc",
        oidc_issuer="https://identity.example.test/",
        oidc_audience="noc-flow-api",
        oidc_jwks_url="https://identity.example.test/.well-known/jwks.json",
    )


def _token(
    private_key,
    *,
    tenant_id: str,
    roles: list[str],
    expires_delta: timedelta = timedelta(minutes=5),
) -> str:
    now = datetime.now(UTC)
    return jwt.encode(
        {
            "iss": "https://identity.example.test/",
            "aud": "noc-flow-api",
            "sub": "operator@example.test",
            "iat": now,
            "exp": now + expires_delta,
            "tenant_id": tenant_id,
            "roles": roles,
        },
        private_key,
        algorithm="RS256",
        headers={"kid": "unit-test"},
    )


def test_role_permissions_follow_least_privilege() -> None:
    viewer = permissions_for_roles(frozenset({Role.VIEWER}))
    operator = permissions_for_roles(frozenset({Role.OPERATOR}))

    assert viewer == frozenset({Permission.INCIDENT_READ})
    assert Permission.INCIDENT_CREATE in operator
    assert Permission.INCIDENT_UPDATE in operator
    assert Permission.INCIDENT_NORMALIZE in operator


def test_permission_dependency_returns_403_for_viewer_write() -> None:
    context = RequestContext(
        tenant_id=UUID("00000000-0000-4000-8000-000000000123"),
        actor_subject="viewer@example.test",
        roles=frozenset({Role.VIEWER}),
    )
    dependency = require_permission(Permission.INCIDENT_CREATE)

    with pytest.raises(AppError) as exc_info:
        dependency(context)

    assert exc_info.value.status_code == 403
    assert exc_info.value.code == "AUTH_FORBIDDEN"


def test_oidc_mode_without_bearer_returns_consistent_401() -> None:
    with pytest.raises(AppError) as exc_info:
        get_request_context(
            credentials=None,
            session=None,  # type: ignore[arg-type]
            settings=_settings(),
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.code == "AUTH_REQUIRED"


def test_oidc_configuration_is_fail_closed_when_required_values_are_missing() -> None:
    with pytest.raises(IdentityProviderConfigurationError):
        OidcConfiguration.from_settings(Settings(environment="test", auth_mode="oidc"))


def test_oidc_validator_accepts_signed_token_and_extracts_trusted_context() -> None:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    tenant_id = UUID("00000000-0000-4000-8000-000000000123")
    token = _token(
        private_key,
        tenant_id=str(tenant_id),
        roles=[Role.OPERATOR.value],
    )

    context = OidcTokenValidator(
        _settings(),
        jwk_client=FakeJwkClient(private_key.public_key()),
    ).validate(token)

    assert context.tenant_id == tenant_id
    assert context.actor_subject == "operator@example.test"
    assert context.roles == frozenset({Role.OPERATOR})
    assert context.has_permission(Permission.INCIDENT_UPDATE)


def test_oidc_validator_rejects_expired_token() -> None:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    token = _token(
        private_key,
        tenant_id="00000000-0000-4000-8000-000000000123",
        roles=[Role.OPERATOR.value],
        expires_delta=timedelta(minutes=-1),
    )

    with pytest.raises(AuthenticationError):
        OidcTokenValidator(
            _settings(),
            jwk_client=FakeJwkClient(private_key.public_key()),
        ).validate(token)


def test_oidc_validator_rejects_unknown_role_and_invalid_tenant() -> None:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    validator = OidcTokenValidator(
        _settings(),
        jwk_client=FakeJwkClient(private_key.public_key()),
    )

    invalid_role = _token(
        private_key,
        tenant_id="00000000-0000-4000-8000-000000000123",
        roles=["Root"],
    )
    invalid_tenant = _token(
        private_key,
        tenant_id="not-a-uuid",
        roles=[Role.VIEWER.value],
    )

    with pytest.raises(AuthenticationError):
        validator.validate(invalid_role)
    with pytest.raises(AuthenticationError):
        validator.validate(invalid_tenant)
