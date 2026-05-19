import typer
from sqlmodel import Session

from sports_api.database import engine
from sports_api.importers.runners import run_results_import, run_standings_import

app = typer.Typer()


@app.command()
def import_standings():
    """Import league standings from API-Football."""
    with Session(engine) as session:
        run_standings_import(session)
    typer.echo("League standings imported successfully.")


@app.command()
def import_results():
    """Import league results from API-Football."""
    with Session(engine) as session:
        run_results_import(session)
    typer.echo("League results imported successfully.")


if __name__ == "__main__":
    app()
