from fastapi import APIRouter, Depends
from sqlmodel import Session

from sports_api.database import get_session
from sports_api.services.results_service import get_current_results_data

router = APIRouter()


@router.get("/sports/results/")
def get_results(session: Session = Depends(get_session)) -> dict:
    return get_current_results_data(session)
