from fastapi import APIRouter

from app.core.errors import ProblemDetails
from app.modules.incidents.application.query_http import query_incidents
from app.modules.incidents.presentation.schemas import IncidentListResponse

router = APIRouter()
router.add_api_route(
    "/incidents/query",
    query_incidents,
    methods=["GET"],
    response_model=IncidentListResponse,
    responses={422: {"model": ProblemDetails}},
    tags=["incidents"],
)
