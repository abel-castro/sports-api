from datetime import UTC, datetime, timedelta

from sqlmodel import Session, select

from sports_api.constants import CURRENT_SEASON
from sports_api.data_providers.api_football import (
    AVAILABLE_LEAGUES_WITH_API_FOOTBALL_DATA,
    ApiFootballDataProvider,
)
from sports_api.importers.results_importer import LeagueResultsImporter
from sports_api.importers.standings_importer import LeagueStandingsImporter
from sports_api.models import Result, Team
from sports_api.utils import get_date_30_days_ago


def run_standings_import(session: Session) -> None:
    for team in session.exec(select(Team)).all():
        session.delete(team)
    session.commit()

    data_provider = ApiFootballDataProvider(season=CURRENT_SEASON)
    importer = LeagueStandingsImporter(
        session=session,
        data_provider=data_provider,
        leagues_to_import=AVAILABLE_LEAGUES_WITH_API_FOOTBALL_DATA,
    )
    importer.run()


def run_results_import(session: Session) -> None:
    for result in session.exec(select(Result)).all():
        session.delete(result)
    session.commit()

    data_provider = ApiFootballDataProvider(season=CURRENT_SEASON)
    from_date_string = get_date_30_days_ago().isoformat()
    to_date_string = (datetime.now(UTC) - timedelta(days=1)).date().isoformat()

    importer = LeagueResultsImporter(
        session=session,
        data_provider=data_provider,
        leagues_to_import=AVAILABLE_LEAGUES_WITH_API_FOOTBALL_DATA,
        from_date=from_date_string,
        to_date=to_date_string,
    )
    importer.run()
