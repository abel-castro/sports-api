from sports_api.models import League, Result
from sports_api.schemas.entities import ResultExternalEntity
from sports_api.services.results_service import get_current_results_data, get_latest_matchday


def create_test_data(session):
    premier_league = League(
        name="Premier League",
        slug="english_premier_league",
        logo="https://media-4.api-sports.io/football/leagues/39.png",
    )
    session.add(premier_league)
    session.commit()
    session.refresh(premier_league)
    assert premier_league.id is not None

    session.add(
        Result(
            home_team="Tottenham Hotspur",
            away_team="Arsenal",
            home_score=1,
            away_score=2,
            league_id=premier_league.id,
            matchday=1,
        )
    )
    session.add(
        Result(
            home_team="Man. City",
            away_team="Chelsea",
            home_score=3,
            away_score=5,
            league_id=premier_league.id,
            matchday=1,
        )
    )
    session.add(
        Result(
            home_team="Fulham",
            away_team="Tottenham",
            home_score=3,
            away_score=0,
            league_id=premier_league.id,
            matchday=2,
        )
    )
    session.add(
        Result(
            home_team="Aston Villa",
            away_team="Wolves",
            home_score=2,
            away_score=0,
            league_id=premier_league.id,
            matchday=2,
        )
    )
    session.commit()


def test_get_current_results_data(session):
    create_test_data(session)

    result_3 = ResultExternalEntity(
        homeTeam="Fulham", awayTeam="Tottenham", homeScore=3, awayScore=0, matchday=2
    )
    result_4 = ResultExternalEntity(
        homeTeam="Aston Villa", awayTeam="Wolves", homeScore=2, awayScore=0, matchday=2
    )

    expected_data = {
        "english_premier_league": [
            result_3.model_dump(),
            result_4.model_dump(),
        ]
    }

    assert get_current_results_data(session) == expected_data


def test_get_latest_matchday(session):
    create_test_data(session)
    assert get_latest_matchday(session, league_slug="english_premier_league") == 2


def test_get_latest_matchday__no_results(session):
    assert get_latest_matchday(session, league_slug="english_premier_league") == 0
