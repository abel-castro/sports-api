# Sports Dashboard API

FastAPI service serving football league standings and results. Fetches data from [API-Football](https://www.api-football.com/) and exposes it via a REST API.

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- Docker (for the local Postgres)

## Setup

```bash
cd sports-api

# Install dependencies
uv sync

# Configure environment variables
cp .env.example .env
# Fill in API_FOOTBAL_KEY (RapidAPI key) and IMPORT_TOKEN (any random string)
```

The default `DATABASE_URL` in `.env.example` points at the local Postgres defined in `docker-compose.yml`. To use a managed Postgres (Neon, etc.) instead, change `DATABASE_URL` to its connection string.

## Development

```bash
# Start the local Postgres
docker compose up -d

# Run the API (creates tables on first startup via the lifespan)
uv run fastapi dev src/sports_api/main.py --port 8001

# Run tests (use SQLite in-memory, no Postgres needed)
uv run pytest

# Lint and format
uv run ruff check src tests
uv run ruff format src tests
```

## Pre-commit hooks (prek)

[prek](https://prek.dev) runs ruff, ty, and pytest before each commit. It is configured in `.pre-commit-config.yaml`.

```bash
# Register the git hook (once per clone)
uv run prek install

# Run all hooks against every file (useful after pulling)
uv run prek run --all-files
```

## Sync jobs

The service pulls league data from API-Football, transforms it, and stores it in Postgres. Two import jobs are available, each callable from the CLI or via an authenticated HTTP endpoint.

The first run requires the schema to exist. Start the API once so the lifespan calls `SQLModel.metadata.create_all(engine)`, then trigger the jobs.

### CLI

```bash
# Import league standings (teams + positions + points)
uv run sports-cli import-standings

# Import league results from the last 30 days
uv run sports-cli import-results
```

### HTTP

```bash
# Standings
curl -X POST http://localhost:8001/internal/import/standings \
  -H "X-Import-Token: $IMPORT_TOKEN"

# Results
curl -X POST http://localhost:8001/internal/import/results \
  -H "X-Import-Token: $IMPORT_TOKEN"
```

In production these HTTP endpoints are called daily by a GitHub Actions cron workflow, which posts to `/internal/import/standings` and `/internal/import/results` with the `X-Import-Token` header.

An in-process scheduler (e.g. APScheduler) is intentionally avoided. If the service ever runs more than one instance, an in-process scheduler would fire the imports multiple times in parallel. Keeping the trigger external (one GitHub Actions runner, one HTTP call) keeps the job exactly-once regardless of how many API instances exist.

## API

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/api/sports/standings/` | GET | none | League standings with latest results |
| `/api/sports/results/` | GET | none | Latest matchday results by league |
| `/internal/import/standings` | POST | `X-Import-Token` | Run the standings import |
| `/internal/import/results` | POST | `X-Import-Token` | Run the results import |
| `/health` | GET | none | Liveness probe, returns `{"status": "ok"}` |
| `/docs` | GET | none | OpenAPI documentation |
