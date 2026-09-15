from fastapi import APIRouter

from app.modules.incidents.presentation.router import router as incidents_router
from app.modules.observability.presentation.router import router as health_router
from app.modules.tenancy.presentation.router import router as auth_router

api_v1_router = APIRouter()
api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(incidents_router)
