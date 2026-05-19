from pydantic import BaseModel


class TeamExternalEntity(BaseModel):
    position: int
    name: str
    points: int
    logo: str | None = None


class TeamInternalEntity(TeamExternalEntity):
    id: int | None = None
    data_provider_id: int | None = None


class ResultExternalEntity(BaseModel):
    homeTeam: str
    awayTeam: str
    homeScore: int
    awayScore: int
    matchday: int


class LeagueExternalEntity(BaseModel):
    name: str
    slug: str
    teams: list[TeamExternalEntity] = []
    logo: str | None = None
    results: list[ResultExternalEntity] | None = []


class LeagueInternalEntity(LeagueExternalEntity):
    id: int | None = None
    data_provider_id: int | None = None
    teams: list[TeamInternalEntity] = []


class ResultInternalEntity(ResultExternalEntity):
    id: int | None = None
    data_provider_league_id: int | None = None


class AvailableLeaguesEntity(BaseModel):
    english_premier_league: LeagueInternalEntity
    spanish_la_liga: LeagueInternalEntity
    italian_seria_a: LeagueInternalEntity
    german_bundesliga: LeagueInternalEntity
    french_ligue_1: LeagueInternalEntity
    portuguese_primeira_liga: LeagueInternalEntity


class AvailableResultsEntity(BaseModel):
    english_premier_league: list[ResultExternalEntity] | None = []
    spanish_la_liga: list[ResultExternalEntity] | None = []
    italian_seria_a: list[ResultExternalEntity] | None = []
    german_bundesliga: list[ResultExternalEntity] | None = []
    french_ligue_1: list[ResultExternalEntity] | None = []
    portuguese_primeira_liga: list[ResultExternalEntity] | None = []
