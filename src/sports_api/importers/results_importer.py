from datetime import UTC, datetime

from sqlmodel import Session, select

from sports_api.data_providers.interfaces import DataProviderInterface
from sports_api.models import League, Result
from sports_api.schemas.entities import (
    AvailableLeaguesEntity,
    LeagueInternalEntity,
    ResultInternalEntity,
)


def save_results_data_to_db(
    session: Session, results_data: list[ResultInternalEntity], league: League
) -> None:
    assert league.id is not None
    for result_entity in results_data:
        existing = session.exec(
            select(Result).where(
                Result.home_team == result_entity.homeTeam,
                Result.away_team == result_entity.awayTeam,
                Result.league_id == league.id,
            )
        ).first()
        if existing:
            existing.home_score = result_entity.homeScore
            existing.away_score = result_entity.awayScore
            existing.matchday = result_entity.matchday
            session.add(existing)
        else:
            result = Result(
                home_team=result_entity.homeTeam,
                away_team=result_entity.awayTeam,
                home_score=result_entity.homeScore,
                away_score=result_entity.awayScore,
                matchday=result_entity.matchday,
                league_id=league.id,
            )
            session.add(result)
        league.updated_at = datetime.now(UTC)
        session.add(league)
    session.commit()


class LeagueResultsImporter:
    def __init__(
        self,
        session: Session,
        data_provider: DataProviderInterface,
        leagues_to_import: AvailableLeaguesEntity,
        from_date: str,
        to_date: str,
    ) -> None:
        self.session = session
        self.data_provider = data_provider
        self.leagues_to_import = leagues_to_import
        self.from_date = from_date
        self.to_date = to_date

    def get_or_create_league(self, league_slug: str, league_data: LeagueInternalEntity) -> League:
        league = self.session.exec(select(League).where(League.slug == league_slug)).first()
        if not league:
            league = League(
                slug=league_slug,
                name=league_data.name,
                logo=league_data.logo,
            )
            self.session.add(league)
            self.session.commit()
            self.session.refresh(league)
        return league

    def run(self) -> None:
        for league_to_import in self.leagues_to_import:
            league_slug = league_to_import[0]
            league_entity = league_to_import[1]
            league_instance = self.get_or_create_league(
                league_slug=league_slug, league_data=league_entity
            )
            assert league_entity.data_provider_id is not None
            raw_data = self.data_provider.get_raw_results_data(
                league_data_provider_id=league_entity.data_provider_id,
                from_date=self.from_date,
                to_date=self.to_date,
            )
            result_entities = self.data_provider.transform_raw_results_data_to_entities(
                provider_data=raw_data
            )
            save_results_data_to_db(
                session=self.session,
                results_data=result_entities,
                league=league_instance,
            )
