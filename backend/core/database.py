from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.core.config import settings


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    future=True,
    connect_args={"options": "-c statement_timeout=30000 -c lock_timeout=15000"},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
