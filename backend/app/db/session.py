from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.app.core.config import settings

engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

# Force model registration before the first Session use so SQLAlchemy can resolve relationships.
import backend.app.db.base  # noqa: E402,F401


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
