from sqlmodel import select

from sports_api.data_providers.interfaces import DataProviderInterface
from sports_api.importers.standings_importer import (
    LeagueStandingsImporter,
    save_team_data_to_db,
)
from sports_api.models import League, Team
from sports_api.schemas.entities import (
    AvailableLeaguesEntity,
    LeagueInternalEntity,
    ResultInternalEntity,
    TeamInternalEntity,
)
from tests.test_data import TEST_TEAM_STANDINGS_ENTITY_LIST


def test_save_team_data_to_db(session):
    premier_league = League(
        name="Premier League",
        slug="english_premier_league",
        logo="https://media-4.api-sports.io/football/leagues/39.png",
    )
    session.add(premier_league)
    session.commit()
    session.refresh(premier_league)

    assert len(session.exec(select(League)).all()) == 1
    assert len(session.exec(select(Team)).all()) == 0

    save_team_data_to_db(
        session=session,
        team_data=TEST_TEAM_STANDINGS_ENTITY_LIST,
        league=premier_league,
    )

    assert len(session.exec(select(League)).all()) == 1
    assert len(session.exec(select(Team)).all()) == 4


def test_save_team_data_to_db_updates_existing(session):
    premier_league = League(
        name="Premier League",
        slug="english_premier_league",
    )
    session.add(premier_league)
    session.commit()
    session.refresh(premier_league)

    save_team_data_to_db(
        session=session,
        team_data=TEST_TEAM_STANDINGS_ENTITY_LIST,
        league=premier_league,
    )

    updated_data = [
        TeamInternalEntity(
            name="Tottenham",
            data_provider_id=47,
            points=99,
            position=5,
            logo="https://example.com/new-logo.png",
        ),
    ]
    save_team_data_to_db(session=session, team_data=updated_data, league=premier_league)

    teams = session.exec(select(Team)).all()
    assert len(teams) == 4
    tottenham = next(t for t in teams if t.name == "Tottenham")
    assert tottenham.points == 99
    assert tottenham.position == 5
    assert tottenham.logo == "https://example.com/new-logo.png"


def test_save_team_data_to_db_empty_does_not_touch_league(session):
    premier_league = League(
        name="Premier League",
        slug="english_premier_league",
    )
    session.add(premier_league)
    session.commit()
    session.refresh(premier_league)
    assert premier_league.updated_at is None

    save_team_data_to_db(session=session, team_data=[], league=premier_league)

    session.refresh(premier_league)
    assert premier_league.updated_at is None
    assert len(session.exec(select(Team)).all()) == 0


class StubDataProvider(DataProviderInterface):
    def __init__(self, standings_by_league: dict[int, list[TeamInternalEntity]]) -> None:
        super().__init__(season=2025)
        self._standings_by_league = standings_by_league
        self.calls: list[int] = []

    def get_raw_standings_data(self, league_data_provider_id: int) -> dict:
        self.calls.append(league_data_provider_id)
        return {"league_data_provider_id": league_data_provider_id}

    def transform_raw_standings_data_to_entities(
        self, provider_data: dict
    ) -> list[TeamInternalEntity]:
        return self._standings_by_league.get(provider_data["league_data_provider_id"], [])

    def get_raw_results_data(
        self, league_data_provider_id: int, from_date: str, to_date: str
    ) -> dict:
        raise NotImplementedError

    def transform_raw_results_data_to_entities(
        self, provider_data: dict
    ) -> list[ResultInternalEntity]:
        raise NotImplementedError


def _minimal_available_leagues() -> AvailableLeaguesEntity:
    return AvailableLeaguesEntity(
        english_premier_league=LeagueInternalEntity(
            name="Premier League", slug="english_premier_league", data_provider_id=39
        ),
        spanish_la_liga=LeagueInternalEntity(
            name="La Liga", slug="spanish_la_liga", data_provider_id=140
        ),
        italian_seria_a=LeagueInternalEntity(
            name="Serie A", slug="italian_seria_a", data_provider_id=135
        ),
        german_bundesliga=LeagueInternalEntity(
            name="Bundesliga", slug="german_bundesliga", data_provider_id=78
        ),
        french_ligue_1=LeagueInternalEntity(
            name="Ligue 1", slug="french_ligue_1", data_provider_id=61
        ),
        portuguese_primeira_liga=LeagueInternalEntity(
            name="Primeira Liga",
            slug="portuguese_primeira_liga",
            data_provider_id=94,
        ),
    )


def test_league_standings_importer_run_creates_leagues_and_teams(session):
    leagues = _minimal_available_leagues()
    provider = StubDataProvider(standings_by_league={39: TEST_TEAM_STANDINGS_ENTITY_LIST})

    importer = LeagueStandingsImporter(
        session=session, data_provider=provider, leagues_to_import=leagues
    )
    importer.run()

    all_leagues = session.exec(select(League)).all()
    assert {league.slug for league in all_leagues} == {
        "english_premier_league",
        "spanish_la_liga",
        "italian_seria_a",
        "german_bundesliga",
        "french_ligue_1",
        "portuguese_primeira_liga",
    }
    assert sorted(provider.calls) == [39, 61, 78, 94, 135, 140]

    teams = session.exec(select(Team)).all()
    assert len(teams) == 4
    assert {team.name for team in teams} == {
        "Tottenham",
        "Arsenal",
        "Manchester City",
        "Liverpool",
    }


def test_league_standings_importer_run_reuses_existing_league(session):
    existing = League(name="Old Name", slug="english_premier_league")
    session.add(existing)
    session.commit()

    leagues = _minimal_available_leagues()
    provider = StubDataProvider(standings_by_league={})

    importer = LeagueStandingsImporter(
        session=session, data_provider=provider, leagues_to_import=leagues
    )
    importer.run()

    epl_rows = session.exec(select(League).where(League.slug == "english_premier_league")).all()
    assert len(epl_rows) == 1
    assert epl_rows[0].name == "Old Name"
