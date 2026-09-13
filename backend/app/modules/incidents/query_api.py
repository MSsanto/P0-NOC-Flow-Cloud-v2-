from app.core.errors import ProblemDetails
from app.modules.incidents.application.query_http import query_incidents
from app.modules.incidents.presentation.router import router
from app.modules.incidents.presentation.schemas import IncidentListResponse

router.add_api_route(
    "/query",
    query_incidents,
    methods=["GET"],
    response_model=IncidentListResponse,
    responses={422: {"model": ProblemDetails}},
    tags=["incidents"],
)
router.routes.insert(0, router.routes.pop())
