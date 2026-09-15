from dataclasses import dataclass
from typing import Any
from uuid import UUID

import jwt
from jwt import PyJWKClient
from jwt.exceptions import PyJWTError

from app.core.config import Settings
from app.modules.tenancy.application.context import RequestContext
from app.modules.tenancy.application.security import Role


class IdentityProviderConfigurationError(RuntimeError):
    pass


class AuthenticationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class OidcConfiguration:
    issuer: str
    audience: str
    jwks_url: str
    algorithms: tuple[str, ...]
    tenant_claim: str
    roles_claim: str
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
            roles_claim=settings.oidc_roles_claim,
            leeway_seconds=settings.oidc_leeway_seconds,
        )


class OidcTokenValidator:
    def __init__(self, settings: Settings, jwk_client: PyJWKClient | None = None) -> None:
        self.config = OidcConfiguration.from_settings(settings)
        self.jwk_client = jwk_client or PyJWKClient(self.config.jwks_url)

    def validate(self, token: str) -> RequestContext:
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
        except (PyJWTError, OSError, ValueError) as exc:
            raise AuthenticationError("Bearer token validation failed.") from exc

        return self._request_context_from_claims(claims)

    def _request_context_from_claims(self, claims: dict[str, Any]) -> RequestContext:
        subject = claims.get("sub")
        if not isinstance(subject, str) or not subject.strip():
            raise AuthenticationError("Token subject claim is invalid.")

        raw_tenant = claims.get(self.config.tenant_claim)
        try:
            tenant_id = UUID(str(raw_tenant))
        except (TypeError, ValueError) as exc:
            raise AuthenticationError("Token tenant claim is invalid.") from exc

        raw_roles = claims.get(self.config.roles_claim)
        if isinstance(raw_roles, str):
            role_values = [raw_roles]
        elif isinstance(raw_roles, list) and all(isinstance(item, str) for item in raw_roles):
            role_values = raw_roles
        else:
            raise AuthenticationError("Token roles claim is invalid.")

        try:
            roles = frozenset(Role(value) for value in role_values)
        except ValueError as exc:
            raise AuthenticationError("Token contains an unsupported role.") from exc
        if not roles:
            raise AuthenticationError("Token must contain at least one role.")

        return RequestContext(
            tenant_id=tenant_id,
            actor_subject=subject.strip(),
            roles=roles,
        )
