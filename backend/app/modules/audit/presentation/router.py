from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.modules.audit.infrastructure.repository import SqlAlchemyAuditRepository
from app.modules.audit.presentation.schemas import AuditEventPage, AuditEventResponse
from app.modules.tenancy.application.context import RequestContext
from app.modules.tenancy.application.security import Permission
from app.modules.tenancy.presentation.dependencies import require_permission

router = APIRouter(prefix="/audit-events", tags=["audit"])


@router.get("", response_model=AuditEventPage)
def list_audit_events(
    session: Annotated[Session, Depends(get_db_session)],
    context: Annotated[RequestContext, Depends(require_permission(Permission.AUDIT_READ))],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 25,
    action: Annotated[str | None, Query(min_length=1, max_length=64)] = None,
    resource_type: Annotated[str | None, Query(min_length=1, max_length=64)] = None,
) -> AuditEventPage:
    items, total = SqlAlchemyAuditRepository(session).list_for_tenant(
        context.tenant_id,
        page=page,
        page_size=page_size,
        action=action,
        resource_type=resource_type,
    )
    return AuditEventPage(
        items=[AuditEventResponse.model_validate(item) for item in items],
        page=page,
        page_size=page_size,
        total=total,
    )
