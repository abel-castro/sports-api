from sqlmodel import select

from sports_api.data_providers.interfaces import DataProviderInterface
from sports_api.importers.results_importer import (
    LeagueResultsImporter,
    save_results_data_to_db,
)
from sports_api.models import League, Result
from sports_api.schemas.entities import (
    AvailableLeaguesEntity,
    LeagueInternalEntity,
    ResultInternalEntity,
    TeamInternalEntity,
)
from tests.test_data import TEST_RESULT_ENTITY_LIST


def test_save_results_data_to_db(session):
    premier_league = League(
        name="Premier League",
        slug="english_premier_league",
        logo="https://media-4.api-sports.io/football/leagues/39.png",
    )
    session.add(premier_league)
    session.commit()
    session.refresh(premier_league)

    save_results_data_to_db(
        session=session,
        results_data=TEST_RESULT_ENTITY_LIST,
        league=premier_league,
    )

    results = session.exec(select(Result)).all()
    assert len(results) == len(TEST_RESULT_ENTITY_LIST)
    session.refresh(premier_league)
    assert premier_league.updated_at is not None


def test_save_results_data_to_db_updates_existing(session):
    premier_league = League(
        name="Premier League",
        slug="english_premier_league",
    )
    session.add(premier_league)
    session.commit()
    session.refresh(premier_league)

    save_results_data_to_db(
        session=session,
        results_data=TEST_RESULT_ENTITY_LIST,
        league=premier_league,
    )

    updated_data = [
        ResultInternalEntity(
            homeTeam="Bournemouth",
            awayTeam="Luton",
            homeScore=9,
            awayScore=0,
            matchday=99,
            id=None,
            data_provider_league_id=39,
        ),
    ]
    save_results_data_to_db(session=session, results_data=updated_data, league=premier_league)

    results = session.exec(select(Result)).all()
    assert len(results) == len(TEST_RESULT_ENTITY_LIST)
    match = next(r for r in results if r.home_team == "Bournemouth" and r.away_team == "Luton")
    assert match.home_score == 9
    assert match.away_score == 0
    assert match.matchday == 99


class StubDataProvider(DataProviderInterface):
    def __init__(self, results_by_league: dict[int, list[ResultInternalEntity]]) -> None:
        super().__init__(season=2025)
        self._results_by_league = results_by_league
        self.calls: list[tuple[int, str, str]] = []

    def get_raw_standings_data(self, league_data_provider_id: int) -> dict:
        raise NotImplementedError

    def transform_raw_standings_data_to_entities(
        self, provider_data: dict
    ) -> list[TeamInternalEntity]:
        raise NotImplementedError

    def get_raw_results_data(
        self, league_data_provider_id: int, from_date: str, to_date: str
    ) -> dict:
        self.calls.append((league_data_provider_id, from_date, to_date))
        return {"league_data_provider_id": league_data_provider_id}

    def transform_raw_results_data_to_entities(
        self, provider_data: dict
    ) -> list[ResultInternalEntity]:
        return self._results_by_league.get(provider_data["league_data_provider_id"], [])


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


def test_league_results_importer_run_creates_leagues_and_results(session):
    leagues = _minimal_available_leagues()
    provider = StubDataProvider(results_by_league={39: TEST_RESULT_ENTITY_LIST})

    importer = LeagueResultsImporter(
        session=session,
        data_provider=provider,
        leagues_to_import=leagues,
        from_date="2026-04-01",
        to_date="2026-05-01",
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
    assert sorted(provider.calls) == [
        (39, "2026-04-01", "2026-05-01"),
        (61, "2026-04-01", "2026-05-01"),
        (78, "2026-04-01", "2026-05-01"),
        (94, "2026-04-01", "2026-05-01"),
        (135, "2026-04-01", "2026-05-01"),
        (140, "2026-04-01", "2026-05-01"),
    ]

    results = session.exec(select(Result)).all()
    assert len(results) == len(TEST_RESULT_ENTITY_LIST)


def test_league_results_importer_run_reuses_existing_league(session):
    existing = League(name="Old Name", slug="english_premier_league")
    session.add(existing)
    session.commit()

    leagues = _minimal_available_leagues()
    provider = StubDataProvider(results_by_league={})

    importer = LeagueResultsImporter(
        session=session,
        data_provider=provider,
        leagues_to_import=leagues,
        from_date="2026-04-01",
        to_date="2026-05-01",
    )
    importer.run()

    epl_rows = session.exec(select(League).where(League.slug == "english_premier_league")).all()
    assert len(epl_rows) == 1
    assert epl_rows[0].name == "Old Name"
