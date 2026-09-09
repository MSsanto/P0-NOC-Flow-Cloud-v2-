from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.db.session import get_db_session
from app.modules.tenancy.application.context import RequestContext
from app.modules.tenancy.infrastructure.demo_provider import (
    DemoContextUnavailableError,
    resolve_demo_context,
)


def get_request_context(
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> RequestContext:
    try:
        return resolve_demo_context(session, settings)
    except DemoContextUnavailableError as exc:
        raise AppError(
            status_code=503,
            title="Identity context unavailable",
            detail="No authorized identity provider is configured for this environment.",
            code="IDENTITY_CONTEXT_UNAVAILABLE",
            problem_slug="identity-context-unavailable",
        ) from exc
