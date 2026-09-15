from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.db.session import get_db_session
from app.modules.tenancy.application.context import RequestContext
from app.modules.tenancy.application.security import Permission
from app.modules.tenancy.infrastructure.demo_provider import (
    DemoContextUnavailableError,
    resolve_demo_context,
)
from app.modules.tenancy.infrastructure.models import TenantModel
from app.modules.tenancy.infrastructure.oidc_provider import (
    AuthenticationError,
    IdentityProviderConfigurationError,
    OidcTokenValidator,
)

_bearer = HTTPBearer(auto_error=False)


def _auth_required() -> AppError:
    return AppError(
        status_code=401,
        title="Authentication required",
        detail="A valid Bearer token is required.",
        code="AUTH_REQUIRED",
        problem_slug="authentication-required",
    )


def _invalid_token() -> AppError:
    return AppError(
        status_code=401,
        title="Invalid authentication token",
        detail="The supplied Bearer token is invalid or expired.",
        code="AUTH_INVALID_TOKEN",
        problem_slug="invalid-authentication-token",
    )


def get_request_context(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> RequestContext:
    if settings.auth_mode == "demo":
        try:
            return resolve_demo_context(session, settings)
        except DemoContextUnavailableError as exc:
            raise AppError(
                status_code=503,
                title="Identity context unavailable",
                detail="Demo identity is disabled outside development and test.",
                code="IDENTITY_CONTEXT_UNAVAILABLE",
                problem_slug="identity-context-unavailable",
            ) from exc

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _auth_required()

    try:
        context = OidcTokenValidator(settings).validate(credentials.credentials)
    except IdentityProviderConfigurationError as exc:
        raise AppError(
            status_code=503,
            title="Identity provider unavailable",
            detail="OIDC authentication is not configured correctly for this environment.",
            code="IDENTITY_PROVIDER_UNAVAILABLE",
            problem_slug="identity-provider-unavailable",
        ) from exc
    except AuthenticationError as exc:
        raise _invalid_token() from exc

    tenant = session.get(TenantModel, context.tenant_id)
    if tenant is None or not tenant.is_active:
        raise AppError(
            status_code=403,
            title="Tenant access denied",
            detail="The authenticated identity is not authorized for an active tenant.",
            code="TENANT_ACCESS_DENIED",
            problem_slug="tenant-access-denied",
        )
    return context


def require_permission(
    permission: Permission,
) -> Callable[..., RequestContext]:
    def dependency(
        context: Annotated[RequestContext, Depends(get_request_context)],
    ) -> RequestContext:
        if not context.has_permission(permission):
            raise AppError(
                status_code=403,
                title="Permission denied",
                detail="The authenticated identity does not have permission for this action.",
                code="AUTH_FORBIDDEN",
                problem_slug="permission-denied",
            )
        return context

    return dependency
