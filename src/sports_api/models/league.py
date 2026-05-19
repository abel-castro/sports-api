from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from sports_api.models.result import Result
    from sports_api.models.team import Team


class League(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    slug: str = Field(max_length=100)
    logo: str | None = None
    updated_at: datetime | None = None

    teams: list["Team"] = Relationship(back_populates="league")
    results: list["Result"] = Relationship(back_populates="league")
