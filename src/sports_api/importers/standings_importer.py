from datetime import UTC, datetime

from sqlmodel import Session, select

from sports_api.data_providers.interfaces import DataProviderInterface
from sports_api.models import League, Team
from sports_api.schemas.entities import (
    AvailableLeaguesEntity,
    LeagueInternalEntity,
    TeamInternalEntity,
)


def save_team_data_to_db(
    session: Session, team_data: list[TeamInternalEntity], league: League
) -> None:
    assert league.id is not None
    for team_entity in team_data:
        existing = session.exec(
            select(Team).where(Team.name == team_entity.name, Team.league_id == league.id)
        ).first()
        if existing:
            existing.position = team_entity.position
            existing.points = team_entity.points
            existing.logo = team_entity.logo
            session.add(existing)
        else:
            team = Team(
                name=team_entity.name,
                position=team_entity.position,
                points=team_entity.points,
                logo=team_entity.logo,
                league_id=league.id,
            )
            session.add(team)
    if team_data:
        league.updated_at = datetime.now(UTC)
        session.add(league)
    session.commit()


class LeagueStandingsImporter:
    def __init__(
        self,
        session: Session,
        data_provider: DataProviderInterface,
        leagues_to_import: AvailableLeaguesEntity,
    ) -> None:
        self.session = session
        self.data_provider = data_provider
        self.leagues_to_import = leagues_to_import

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
            raw_data = self.data_provider.get_raw_standings_data(
                league_data_provider_id=league_entity.data_provider_id
            )
            team_entities = self.data_provider.transform_raw_standings_data_to_entities(
                provider_data=raw_data
            )
            save_team_data_to_db(
                session=self.session,
                team_data=team_entities,
                league=league_instance,
            )
