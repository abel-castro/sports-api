import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from sports_api.config import settings
from sports_api.database import get_session
from sports_api.main import app
from sports_api.models import League, Result, Team  # noqa: F401


def get_test_session():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_session] = get_test_session
client = TestClient(app)


def test_get_standings_empty():
    response = client.get("/api/sports/standings/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_results_empty():
    response = client.get("/api/sports/results/")
    assert response.status_code == 200
    assert response.json() == {}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.fixture
def import_token(monkeypatch):
    token = "test-token"
    monkeypatch.setattr(settings, "import_token", token)
    return token


def test_trigger_standings_import_unauthorized():
    response = client.post("/internal/import/standings")
    assert response.status_code == 401


def test_trigger_standings_import_wrong_token(import_token):
    response = client.post("/internal/import/standings", headers={"X-Import-Token": "wrong"})
    assert response.status_code == 401


def test_trigger_standings_import_ok(import_token, monkeypatch):
    called = {}

    def fake_run(session):
        called["standings"] = True

    monkeypatch.setattr("sports_api.main.run_standings_import", fake_run)
    response = client.post("/internal/import/standings", headers={"X-Import-Token": import_token})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert called == {"standings": True}


def test_trigger_results_import_unauthorized():
    response = client.post("/internal/import/results")
    assert response.status_code == 401


def test_trigger_results_import_ok(import_token, monkeypatch):
    called = {}

    def fake_run(session):
        called["results"] = True

    monkeypatch.setattr("sports_api.main.run_results_import", fake_run)
    response = client.post("/internal/import/results", headers={"X-Import-Token": import_token})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert called == {"results": True}
