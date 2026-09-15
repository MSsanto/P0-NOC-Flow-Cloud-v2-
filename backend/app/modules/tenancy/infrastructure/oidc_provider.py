from dataclasses import dataclass
from typing import Any
from uuid import UUID

import jwt
from jwt import PyJWKClient
from jwt.exceptions import PyJWKClientError, PyJWTError

from app.core.config import Settings


class IdentityProviderConfigurationError(RuntimeError):
    pass


class AuthenticationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ExternalIdentity:
    subject: str
    requested_tenant_id: UUID


@dataclass(frozen=True, slots=True)
class OidcConfiguration:
    issuer: str
    audience: str
    jwks_url: str
    algorithms: tuple[str, ...]
    tenant_claim: str
    leeway_seconds: int

    @classmethod
    def from_settings(cls, settings: Settings) -> "OidcConfiguration":
        if not settings.oidc_issuer or not settings.oidc_audience or not settings.oidc_jwks_url:
            raise IdentityProviderConfigurationError(
                "OIDC issuer, audience and JWKS URL must be configured."
            )
        if not settings.oidc_algorithms:
            raise IdentityProviderConfigurationError(
                "At least one trusted OIDC signing algorithm must be configured."
            )
        return cls(
            issuer=settings.oidc_issuer,
            audience=settings.oidc_audience,
            jwks_url=settings.oidc_jwks_url,
            algorithms=tuple(settings.oidc_algorithms),
            tenant_claim=settings.oidc_tenant_claim,
            leeway_seconds=settings.oidc_leeway_seconds,
        )


class OidcTokenValidator:
    def __init__(self, settings: Settings, jwk_client: PyJWKClient | None = None) -> None:
        self.config = OidcConfiguration.from_settings(settings)
        self.jwk_client = jwk_client or PyJWKClient(self.config.jwks_url)

    def validate(self, token: str) -> ExternalIdentity:
        try:
            signing_key = self.jwk_client.get_signing_key_from_jwt(token).key
            claims = jwt.decode(
                token,
                signing_key,
                algorithms=list(self.config.algorithms),
                audience=self.config.audience,
                issuer=self.config.issuer,
                leeway=self.config.leeway_seconds,
                options={"require": ["exp", "iat", "iss", "aud", "sub"]},
            )
        except (PyJWKClientError, PyJWTError, OSError, ValueError) as exc:
            raise AuthenticationError("Bearer token validation failed.") from exc

        return self._external_identity_from_claims(claims)

    def _external_identity_from_claims(self, claims: dict[str, Any]) -> ExternalIdentity:
        subject = claims.get("sub")
        if not isinstance(subject, str) or not subject.strip():
            raise AuthenticationError("Token subject claim is invalid.")

        raw_tenant = claims.get(self.config.tenant_claim)
        try:
            tenant_id = UUID(str(raw_tenant))
        except (TypeError, ValueError) as exc:
            raise AuthenticationError("Token tenant claim is invalid.") from exc

        return ExternalIdentity(
            subject=subject.strip(),
            requested_tenant_id=tenant_id,
        )
