from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from sports_api.models.league import League


class Result(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    home_team: str = Field(max_length=100)
    away_team: str = Field(max_length=100)
    home_score: int
    away_score: int
    matchday: int
    league_id: int = Field(foreign_key="league.id")

    league: Optional["League"] = Relationship(back_populates="results")
