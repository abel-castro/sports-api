from sqlmodel import Session, create_engine

from sports_api.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=1800,
)


def get_session():
    with Session(engine) as session:
        yield session
