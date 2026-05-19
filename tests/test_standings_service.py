from typing import TypedDict

from sports_api.models import League, Team
from sports_api.schemas.entities import LeagueExternalEntity, TeamExternalEntity
from sports_api.services.standings_service import get_current_standings_data


class TeamTestData(TypedDict):
    position: int
    name: str
    points: int


TEST_PREMIER_LEAGUE_TEAMS: list[TeamTestData] = [
    {"position": 1, "name": "Tottenham Hotspur", "points": 20},
    {"position": 2, "name": "Arsenal", "points": 18},
    {"position": 3, "name": "Man. City", "points": 15},
    {"position": 4, "name": "Man. U", "points": 13},
    {"position": 5, "name": "Newcastle", "points": 12},
    {"position": 6, "name": "Brighton", "points": 10},
    {"position": 7, "name": "Chelsea", "points": 9},
]

TEST_LA_LIGA_TEAMS: list[TeamTestData] = [
    {"position": 1, "name": "FC Barcelona", "points": 20},
    {"position": 2, "name": "Real Madrid", "points": 19},
    {"position": 3, "name": "Girona", "points": 18},
    {"position": 4, "name": "Atlético de Madrid", "points": 16},
    {"position": 5, "name": "Athletic Bilbao", "points": 14},
    {"position": 6, "name": "Villareal", "points": 13},
    {"position": 7, "name": "Real Sociedad", "points": 1},
]


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

    for team in TEST_PREMIER_LEAGUE_TEAMS:
        session.add(
            Team(
                name=team["name"],
                position=team["position"],
                points=team["points"],
                league_id=premier_league.id,
            )
        )

    la_liga = League(
        name="La Liga",
        slug="spanish_la_liga",
        logo="https://media-4.api-sports.io/football/leagues/140.png",
    )
    session.add(la_liga)
    session.commit()
    session.refresh(la_liga)
    assert la_liga.id is not None

    for team in TEST_LA_LIGA_TEAMS:
        session.add(
            Team(
                name=team["name"],
                position=team["position"],
                points=team["points"],
                league_id=la_liga.id,
            )
        )
    session.commit()


def test_get_current_standings_data(session):
    create_test_data(session)

    premier_league = LeagueExternalEntity(
        name="Premier League",
        slug="english_premier_league",
        teams=[TeamExternalEntity(**t) for t in TEST_PREMIER_LEAGUE_TEAMS],
        logo="https://media-4.api-sports.io/football/leagues/39.png",
    )
    la_liga = LeagueExternalEntity(
        name="La Liga",
        slug="spanish_la_liga",
        teams=[TeamExternalEntity(**t) for t in TEST_LA_LIGA_TEAMS],
        logo="https://media-4.api-sports.io/football/leagues/140.png",
    )

    expected_data = [
        premier_league.model_dump(),
        la_liga.model_dump(),
    ]

    assert get_current_standings_data(session) == expected_data
