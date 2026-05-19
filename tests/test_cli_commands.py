from typer.testing import CliRunner

from sports_api.cli import commands
from sports_api.cli.commands import app

runner = CliRunner()


def test_import_standings_command(monkeypatch):
    called = {}

    def fake_run(session):
        called["session"] = session

    monkeypatch.setattr(commands, "run_standings_import", fake_run)

    result = runner.invoke(app, ["import-standings"])

    assert result.exit_code == 0
    assert "League standings imported successfully." in result.stdout
    assert "session" in called


def test_import_results_command(monkeypatch):
    called = {}

    def fake_run(session):
        called["session"] = session

    monkeypatch.setattr(commands, "run_results_import", fake_run)

    result = runner.invoke(app, ["import-results"])

    assert result.exit_code == 0
    assert "League results imported successfully." in result.stdout
    assert "session" in called
