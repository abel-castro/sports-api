from fastapi import APIRouter

from sports_api.api.results import router as results_router
from sports_api.api.standings import router as standings_router

api_router = APIRouter(prefix="/api")
api_router.include_router(standings_router)
api_router.include_router(results_router)
