from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from app.core.config import Settings
from app.modules.tenancy.infrastructure.cloudflare_access_provider import (
    CloudflareAccessConfiguration,
    CloudflareAccessTokenValidator,
)
from app.modules.tenancy.infrastructure.oidc_provider import (
    AuthenticationError,
    IdentityProviderConfigurationError,
)


class FakeJwkClient:
    def __init__(self, public_key) -> None:
        self.public_key = public_key

    def get_signing_key_from_jwt(self, _token: str):
        return SimpleNamespace(key=self.public_key)


def _settings() -> Settings:
    return Settings(
        environment="test",
        auth_mode="cloudflare_access",
        cloudflare_access_team_domain="https://nocflow.cloudflareaccess.com",
        cloudflare_access_audience="test-audience",
    )


def _token(
    private_key,
    *,
    audience: str = "test-audience",
    expires_delta: timedelta = timedelta(minutes=5),
) -> str:
    now = datetime.now(UTC)
    return jwt.encode(
        {
            "iss": "https://nocflow.cloudflareaccess.com",
            "aud": [audience],
            "sub": "cf-user-123",
            "email": "operator@example.test",
            "iat": now,
            "exp": now + expires_delta,
        },
        private_key,
        algorithm="RS256",
        headers={"kid": "cloudflare-unit-test"},
    )


def test_cloudflare_access_configuration_builds_official_certs_endpoint() -> None:
    config = CloudflareAccessConfiguration.from_settings(_settings())

    assert config.jwks_url == (
        "https://nocflow.cloudflareaccess.com/cdn-cgi/access/certs"
    )
    assert config.audience == "test-audience"


def test_cloudflare_access_configuration_fails_closed_without_audience() -> None:
    settings = Settings(
        environment="test",
        auth_mode="cloudflare_access",
        cloudflare_access_team_domain="https://nocflow.cloudflareaccess.com",
    )

    with pytest.raises(IdentityProviderConfigurationError):
        CloudflareAccessConfiguration.from_settings(settings)


def test_cloudflare_access_validator_accepts_signed_identity_token() -> None:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    token = _token(private_key)

    identity = CloudflareAccessTokenValidator(
        _settings(),
        jwk_client=FakeJwkClient(private_key.public_key()),
    ).validate(token)

    assert identity.subject == "cf-user-123"
    assert identity.email == "operator@example.test"


def test_cloudflare_access_validator_rejects_wrong_audience() -> None:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    token = _token(private_key, audience="wrong-app")

    with pytest.raises(AuthenticationError):
        CloudflareAccessTokenValidator(
            _settings(),
            jwk_client=FakeJwkClient(private_key.public_key()),
        ).validate(token)


def test_cloudflare_access_validator_rejects_expired_token() -> None:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    token = _token(private_key, expires_delta=timedelta(minutes=-1))

    with pytest.raises(AuthenticationError):
        CloudflareAccessTokenValidator(
            _settings(),
            jwk_client=FakeJwkClient(private_key.public_key()),
        ).validate(token)
