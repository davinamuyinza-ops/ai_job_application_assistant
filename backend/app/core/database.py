from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


def _with_pg8000_driver(database_url: str) -> str:
    # Supabase (and most providers) hand out a plain "postgresql://" connection
    # string. We use the pure-Python pg8000 driver (no C build step, no
    # pg_config dependency), so rewrite the URL to request it explicitly.
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+pg8000://", 1)
    return database_url


engine = create_engine(_with_pg8000_driver(settings.database_url))

SessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
