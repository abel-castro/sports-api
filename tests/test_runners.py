from sqlmodel import select

from sports_api.importers import runners
from sports_api.importers.runners import run_results_import, run_standings_import
from sports_api.models import League, Result, Team


class FakeImporter:
    instances: list["FakeImporter"] = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.ran = False
        FakeImporter.instances.append(self)

    def run(self) -> None:
        self.ran = True


def _seed_league(session) -> int:
    league = League(name="Premier League", slug="english_premier_league")
    session.add(league)
    session.commit()
    session.refresh(league)
    assert league.id is not None
    return league.id


def test_run_standings_import_clears_existing_teams_and_runs_importer(session, monkeypatch):
    FakeImporter.instances = []
    league_id = _seed_league(session)
    session.add(Team(name="Old Team", position=1, points=10, league_id=league_id))
    session.commit()
    assert len(session.exec(select(Team)).all()) == 1

    monkeypatch.setattr(runners, "ApiFootballDataProvider", lambda season: object())
    monkeypatch.setattr(runners, "LeagueStandingsImporter", FakeImporter)

    run_standings_import(session)

    assert len(session.exec(select(Team)).all()) == 0
    assert len(FakeImporter.instances) == 1
    assert FakeImporter.instances[0].ran is True


def test_run_results_import_clears_existing_results_and_runs_importer(session, monkeypatch):
    FakeImporter.instances = []
    league_id = _seed_league(session)
    session.add(
        Result(
            home_team="A",
            away_team="B",
            home_score=1,
            away_score=0,
            matchday=1,
            league_id=league_id,
        )
    )
    session.commit()
    assert len(session.exec(select(Result)).all()) == 1

    monkeypatch.setattr(runners, "ApiFootballDataProvider", lambda season: object())
    monkeypatch.setattr(runners, "LeagueResultsImporter", FakeImporter)

    run_results_import(session)

    assert len(session.exec(select(Result)).all()) == 0
    assert len(FakeImporter.instances) == 1
    instance = FakeImporter.instances[0]
    assert instance.ran is True
    assert "from_date" in instance.kwargs
    assert "to_date" in instance.kwargs
