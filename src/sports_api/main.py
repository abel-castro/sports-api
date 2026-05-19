from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, SQLModel

from sports_api.api.router import api_router
from sports_api.config import settings
from sports_api.database import engine, get_session
from sports_api.importers.runners import run_results_import, run_standings_import


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(title="Sports Dashboard API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://sports-dashboard.abelcastro.dev",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def require_import_token(x_import_token: str = Header(default="")) -> None:
    expected = settings.import_token
    if not expected or x_import_token != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Import-Token",
        )


@app.post(
    "/internal/import/standings",
    dependencies=[Depends(require_import_token)],
)
def trigger_standings_import(session: Session = Depends(get_session)) -> dict[str, str]:
    run_standings_import(session)
    return {"status": "ok"}


@app.post(
    "/internal/import/results",
    dependencies=[Depends(require_import_token)],
)
def trigger_results_import(session: Session = Depends(get_session)) -> dict[str, str]:
    run_results_import(session)
    return {"status": "ok"}
