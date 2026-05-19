import copy

import requests

from sports_api.config import settings
from sports_api.constants import AVAILABLE_LEAGUES
from sports_api.data_providers.interfaces import DataProviderInterface
from sports_api.schemas.entities import (
    AvailableLeaguesEntity,
    ResultInternalEntity,
    TeamInternalEntity,
)


def add_api_football_related_data() -> AvailableLeaguesEntity:
    available_leagues_with_api_football_data = copy.deepcopy(AVAILABLE_LEAGUES)

    available_leagues_with_api_football_data.english_premier_league.data_provider_id = 39
    available_leagues_with_api_football_data.english_premier_league.logo = (
        "https://media-4.api-sports.io/football/leagues/39.png"
    )

    available_leagues_with_api_football_data.spanish_la_liga.data_provider_id = 140
    available_leagues_with_api_football_data.spanish_la_liga.logo = (
        "https://media-4.api-sports.io/football/leagues/140.png"
    )

    available_leagues_with_api_football_data.italian_seria_a.data_provider_id = 135
    available_leagues_with_api_football_data.italian_seria_a.logo = (
        "https://media-4.api-sports.io/football/leagues/135.png"
    )

    available_leagues_with_api_football_data.german_bundesliga.data_provider_id = 78
    available_leagues_with_api_football_data.german_bundesliga.logo = (
        "https://media-4.api-sports.io/football/leagues/78.png"
    )

    available_leagues_with_api_football_data.french_ligue_1.data_provider_id = 61
    available_leagues_with_api_football_data.french_ligue_1.logo = (
        "https://media-4.api-sports.io/football/leagues/61.png"
    )

    available_leagues_with_api_football_data.portuguese_primeira_liga.data_provider_id = 94
    available_leagues_with_api_football_data.portuguese_primeira_liga.logo = (
        "https://media-4.api-sports.io/football/leagues/94.png"
    )
    return available_leagues_with_api_football_data


AVAILABLE_LEAGUES_WITH_API_FOOTBALL_DATA = add_api_football_related_data()


def transform_provider_standings_data_to_entities(
    provider_data: dict,
) -> list[TeamInternalEntity]:
    result = []
    try:
        league_data = provider_data["response"][0]
        if league_data.get("league").get("standings"):
            for team_data in league_data.get("league").get("standings")[0]:
                team_name = team_data.get("team").get("name")
                team_logo = team_data.get("team").get("logo")
                team_position = team_data.get("rank")
                team_points = team_data.get("points")
                team_id = team_data.get("team").get("id")
                result.append(
                    TeamInternalEntity(
                        name=team_name,
                        logo=team_logo,
                        position=team_position,
                        points=team_points,
                        data_provider_id=team_id,
                    )
                )
    except KeyError:
        pass
    return result


def transform_provider_results_data_to_entities(
    provider_data: dict,
) -> list[ResultInternalEntity]:
    formatted_data = []
    for match in provider_data.get("response") or []:
        teams = match.get("teams")
        goals = match.get("goals")

        home_team = teams.get("home").get("name")
        away_team = teams.get("away").get("name")
        home_goals = goals.get("home")
        away_goals = goals.get("away")
        matchday = int(match.get("league")["round"].split()[3])

        if teams and home_goals is not None and away_goals is not None and matchday:
            league_id = match.get("league").get("id")
            formatted_data.append(
                ResultInternalEntity(
                    homeTeam=home_team,
                    awayTeam=away_team,
                    homeScore=home_goals,
                    awayScore=away_goals,
                    matchday=matchday,
                    data_provider_league_id=league_id,
                )
            )
    return formatted_data


class ApiFootballDataProvider(DataProviderInterface):
    def get_raw_standings_data(self, league_data_provider_id: int) -> dict:
        data = {}
        url = "https://api-football-v1.p.rapidapi.com/v3/standings"

        querystring = {"season": self.season, "league": league_data_provider_id}

        headers = {
            "X-RapidAPI-Key": settings.api_footbal_key,
            "X-RapidAPI-Host": settings.api_footbal_host,
        }

        try:
            response = requests.get(url, headers=headers, params=querystring)
            return response.json()
        except Exception:
            pass

        return data

    def transform_raw_standings_data_to_entities(
        self, provider_data: dict
    ) -> list[TeamInternalEntity]:
        return transform_provider_standings_data_to_entities(provider_data=provider_data)

    def transform_raw_results_data_to_entities(
        self, provider_data: dict
    ) -> list[ResultInternalEntity]:
        return transform_provider_results_data_to_entities(provider_data=provider_data)

    def get_raw_results_data(
        self, league_data_provider_id: int, from_date: str, to_date: str
    ) -> dict:
        data = {}
        url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"

        querystring = {
            "season": self.season,
            "league": league_data_provider_id,
            "from": from_date,
            "to": to_date,
        }

        headers = {
            "X-RapidAPI-Key": settings.api_footbal_key,
            "X-RapidAPI-Host": settings.api_footbal_host,
        }

        try:
            response = requests.get(url, headers=headers, params=querystring)
            return response.json()
        except Exception:
            pass

        return data
