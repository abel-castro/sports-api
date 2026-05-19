from fastapi import APIRouter, Depends
from sqlmodel import Session

from sports_api.database import get_session
from sports_api.services.standings_service import get_current_standings_data

router = APIRouter()


@router.get("/sports/standings/")
def get_standings(session: Session = Depends(get_session)) -> list[dict]:
    return get_current_standings_data(session)
