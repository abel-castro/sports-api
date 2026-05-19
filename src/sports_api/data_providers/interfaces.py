from abc import ABC, abstractmethod

from sports_api.schemas.entities import ResultInternalEntity, TeamInternalEntity


class DataProviderInterface(ABC):
    def __init__(self, season: int) -> None:
        super().__init__()
        self.season = season

    @abstractmethod
    def get_raw_standings_data(self, league_data_provider_id: int): ...

    @abstractmethod
    def get_raw_results_data(self, league_data_provider_id: int, from_date: str, to_date: str): ...

    @abstractmethod
    def transform_raw_standings_data_to_entities(
        self, provider_data: dict
    ) -> list[TeamInternalEntity]: ...

    @abstractmethod
    def transform_raw_results_data_to_entities(
        self, provider_data: dict
    ) -> list[ResultInternalEntity]: ...
