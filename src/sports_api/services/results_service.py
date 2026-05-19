from sqlmodel import Session, func, select

from sports_api.constants import AVAILABLE_LEAGUES
from sports_api.models import League, Result
from sports_api.schemas.entities import ResultExternalEntity


def get_latest_matchday(session: Session, league_slug: str) -> int:
    league = session.exec(select(League).where(League.slug == league_slug)).first()
    if not league:
        return 0

    result = session.exec(
        select(func.max(Result.matchday)).where(Result.league_id == league.id)
    ).one()
    return result or 0


def get_current_results_data(session: Session) -> dict:
    results_data = {}
    for league_slug in AVAILABLE_LEAGUES.model_dump():
        league = session.exec(select(League).where(League.slug == league_slug)).first()
        if not league:
            continue

        latest_matchday = get_latest_matchday(session, league_slug=league_slug)
        results = session.exec(
            select(Result).where(
                Result.league_id == league.id,
                Result.matchday == latest_matchday,
            )
        ).all()

        league_results = [
            ResultExternalEntity(
                homeTeam=result.home_team,
                awayTeam=result.away_team,
                homeScore=result.home_score,
                awayScore=result.away_score,
                matchday=result.matchday,
            ).model_dump()
            for result in results
        ]

        if league_results:
            results_data[league_slug] = league_results

    return results_data
