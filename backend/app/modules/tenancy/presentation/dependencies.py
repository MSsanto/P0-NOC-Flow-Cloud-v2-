from collections.abc import Callable
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.db.session import get_db_session
from app.modules.tenancy.application.context import RequestContext
from app.modules.tenancy.application.security import Permission, Role
from app.modules.tenancy.infrastructure.cloudflare_access_provider import (
    CloudflareAccessIdentity,
    CloudflareAccessTokenValidator,
)
from app.modules.tenancy.infrastructure.demo_provider import (
    DemoContextUnavailableError,
    resolve_demo_context,
)
from app.modules.tenancy.infrastructure.models import (
    TenantMembershipModel,
    TenantModel,
    UserModel,
)
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
        detail="A valid authentication token is required.",
        code="AUTH_REQUIRED",
        problem_slug="authentication-required",
    )


def _invalid_token() -> AppError:
    return AppError(
        status_code=401,
        title="Invalid authentication token",
        detail="The supplied authentication token is invalid or expired.",
        code="AUTH_INVALID_TOKEN",
        problem_slug="invalid-authentication-token",
    )


def _tenant_access_denied() -> AppError:
    return AppError(
        status_code=403,
        title="Tenant access denied",
        detail="The authenticated identity is not authorized for an active tenant.",
        code="TENANT_ACCESS_DENIED",
        problem_slug="tenant-access-denied",
    )


def _identity_provider_unavailable() -> AppError:
    return AppError(
        status_code=503,
        title="Identity provider unavailable",
        detail="Authentication is not configured correctly for this environment.",
        code="IDENTITY_PROVIDER_UNAVAILABLE",
        problem_slug="identity-provider-unavailable",
    )


def _resolve_membership_context(
    session: Session,
    *,
    external_subject: str,
    actor_subject: str,
    tenant_id: UUID,
) -> RequestContext:
    user = session.scalar(
        select(UserModel).where(UserModel.external_subject == external_subject)
    )
    if user is None or not user.is_active:
        raise _tenant_access_denied()

    tenant = session.get(TenantModel, tenant_id)
    membership = session.get(TenantMembershipModel, (tenant_id, user.id))
    if (
        tenant is None
        or not tenant.is_active
        or membership is None
        or not membership.is_active
    ):
        raise _tenant_access_denied()

    try:
        role = Role(membership.role)
    except ValueError as exc:
        raise AppError(
            status_code=503,
            title="Identity context unavailable",
            detail="The internal membership role is invalid.",
            code="IDENTITY_CONTEXT_UNAVAILABLE",
            problem_slug="identity-context-unavailable",
        ) from exc

    return RequestContext(
        tenant_id=tenant_id,
        actor_subject=actor_subject,
        roles=frozenset({role}),
    )


def _bootstrap_cloudflare_admin(
    session: Session,
    settings: Settings,
    identity: CloudflareAccessIdentity,
    tenant_id: UUID,
) -> None:
    bootstrap_email = settings.cloudflare_access_bootstrap_admin_email
    if settings.environment == "production" or not bootstrap_email:
        return
    if identity.email != bootstrap_email.strip().lower():
        return

    tenant = session.get(TenantModel, tenant_id)
    if tenant is None or not tenant.is_active:
        return

    user = session.scalar(
        select(UserModel).where(UserModel.external_subject == identity.subject)
    )
    if user is None:
        user = UserModel(external_subject=identity.subject, is_active=True)
        session.add(user)
        session.flush()

    membership = session.get(TenantMembershipModel, (tenant_id, user.id))
    if membership is None:
        session.add(
            TenantMembershipModel(
                tenant_id=tenant_id,
                user_id=user.id,
                role=Role.ADMIN.value,
                is_active=True,
            )
        )
        session.commit()


def get_request_context(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    cloudflare_access_token: Annotated[
        str | None, Header(alias="Cf-Access-Jwt-Assertion")
    ] = None,
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

    if settings.auth_mode == "cloudflare_access":
        if not cloudflare_access_token:
            raise _auth_required()
        if settings.cloudflare_access_tenant_id is None:
            raise _identity_provider_unavailable()
        try:
            identity = CloudflareAccessTokenValidator(settings).validate(
                cloudflare_access_token
            )
        except IdentityProviderConfigurationError as exc:
            raise _identity_provider_unavailable() from exc
        except AuthenticationError as exc:
            raise _invalid_token() from exc

        _bootstrap_cloudflare_admin(
            session,
            settings,
            identity,
            settings.cloudflare_access_tenant_id,
        )
        return _resolve_membership_context(
            session,
            external_subject=identity.subject,
            actor_subject=identity.email,
            tenant_id=settings.cloudflare_access_tenant_id,
        )

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _auth_required()

    try:
        identity = OidcTokenValidator(settings).validate(credentials.credentials)
    except IdentityProviderConfigurationError as exc:
        raise _identity_provider_unavailable() from exc
    except AuthenticationError as exc:
        raise _invalid_token() from exc

    return _resolve_membership_context(
        session,
        external_subject=identity.subject,
        actor_subject=identity.subject,
        tenant_id=identity.requested_tenant_id,
    )


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
