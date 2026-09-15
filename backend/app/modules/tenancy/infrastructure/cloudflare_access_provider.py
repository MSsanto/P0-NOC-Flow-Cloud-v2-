from dataclasses import dataclass
from typing import Any

import jwt
from jwt import PyJWKClient
from jwt.exceptions import PyJWKClientError, PyJWTError

from app.core.config import Settings
from app.modules.tenancy.infrastructure.oidc_provider import (
    AuthenticationError,
    IdentityProviderConfigurationError,
)


@dataclass(frozen=True, slots=True)
class CloudflareAccessIdentity:
    subject: str
    email: str


@dataclass(frozen=True, slots=True)
class CloudflareAccessConfiguration:
    team_domain: str
    audience: str
    jwks_url: str

    @classmethod
    def from_settings(cls, settings: Settings) -> "CloudflareAccessConfiguration":
        if not settings.cloudflare_access_team_domain or not settings.cloudflare_access_audience:
            raise IdentityProviderConfigurationError(
                "Cloudflare Access team domain and audience must be configured."
            )

        team_domain = settings.cloudflare_access_team_domain.rstrip("/")
        if not team_domain.startswith("https://"):
            raise IdentityProviderConfigurationError(
                "Cloudflare Access team domain must use HTTPS."
            )

        return cls(
            team_domain=team_domain,
            audience=settings.cloudflare_access_audience,
            jwks_url=f"{team_domain}/cdn-cgi/access/certs",
        )


class CloudflareAccessTokenValidator:
    def __init__(
        self,
        settings: Settings,
        jwk_client: PyJWKClient | None = None,
    ) -> None:
        self.config = CloudflareAccessConfiguration.from_settings(settings)
        self.jwk_client = jwk_client or PyJWKClient(self.config.jwks_url)

    def validate(self, token: str) -> CloudflareAccessIdentity:
        try:
            signing_key = self.jwk_client.get_signing_key_from_jwt(token).key
            claims = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                audience=self.config.audience,
                issuer=self.config.team_domain,
                options={"require": ["exp", "iat", "iss", "aud", "sub", "email"]},
            )
        except (PyJWKClientError, PyJWTError, OSError, ValueError) as exc:
            raise AuthenticationError("Cloudflare Access token validation failed.") from exc

        return self._identity_from_claims(claims)

    def _identity_from_claims(self, claims: dict[str, Any]) -> CloudflareAccessIdentity:
        subject = claims.get("sub")
        email = claims.get("email")
        if not isinstance(subject, str) or not subject.strip():
            raise AuthenticationError("Cloudflare Access subject claim is invalid.")
        if not isinstance(email, str) or "@" not in email:
            raise AuthenticationError("Cloudflare Access email claim is invalid.")

        return CloudflareAccessIdentity(
            subject=subject.strip(),
            email=email.strip().lower(),
        )
