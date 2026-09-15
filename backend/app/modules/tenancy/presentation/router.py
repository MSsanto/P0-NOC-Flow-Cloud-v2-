from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.errors import ProblemDetails
from app.modules.tenancy.application.context import RequestContext
from app.modules.tenancy.application.security import permissions_for_roles
from app.modules.tenancy.presentation.dependencies import get_request_context
from app.modules.tenancy.presentation.schemas import AuthContextResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get(
    "/me",
    response_model=AuthContextResponse,
    responses={401: {"model": ProblemDetails}, 403: {"model": ProblemDetails}},
)
def get_auth_context(
    context: Annotated[RequestContext, Depends(get_request_context)],
) -> AuthContextResponse:
    return AuthContextResponse(
        subject=context.actor_subject,
        tenant_id=context.tenant_id,
        roles=sorted(context.roles, key=lambda role: role.value),
        permissions=sorted(
            permissions_for_roles(context.roles),
            key=lambda permission: permission.value,
        ),
    )
