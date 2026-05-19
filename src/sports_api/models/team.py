from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from sports_api.models.league import League


class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=50)
    position: int
    points: int
    logo: str | None = None
    league_id: int = Field(foreign_key="league.id")

    league: Optional["League"] = Relationship(back_populates="teams")
