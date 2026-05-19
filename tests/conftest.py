import pytest
from sqlmodel import Session, SQLModel, create_engine

from sports_api.models import League, Result, Team  # noqa: F401


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
