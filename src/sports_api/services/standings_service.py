from sqlmodel import Session, col, select

from sports_api.constants import AVAILABLE_LEAGUES
from sports_api.models import League, Result, Team
from sports_api.schemas.entities import (
    LeagueExternalEntity,
    ResultExternalEntity,
    TeamExternalEntity,
)
from sports_api.services.results_service import get_latest_matchday


def get_current_standings_data(session: Session) -> list[dict]:
    leagues_data = []
    for league_slug in AVAILABLE_LEAGUES.model_dump():
        league = session.exec(select(League).where(League.slug == league_slug)).first()
        if not league:
            league = League(slug=league_slug, name="")
            session.add(league)
            session.commit()
            session.refresh(league)

        teams = session.exec(
            select(Team).where(Team.league_id == league.id).order_by(col(Team.position))
        ).all()

        league_teams = [
            TeamExternalEntity(
                name=team.name,
                position=team.position,
                points=team.points,
                logo=team.logo,
            ).model_dump()
            for team in teams
        ]

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

        if league.name and league_teams:
            leagues_data.append(
                LeagueExternalEntity(
                    name=league.name,
                    slug=league.slug,
                    teams=league_teams,
                    logo=league.logo,
                    results=league_results,
                ).model_dump()
            )

    return leagues_data
