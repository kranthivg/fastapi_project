"""Create a fresh SQLite development DB only. Use Alembic for PostgreSQL."""

from . import models  # noqa: F401
from .database import Base, engine

if __name__ == "__main__":
    if engine.dialect.name != "sqlite":
        raise SystemExit("Use alembic upgrade head for PostgreSQL")
    Base.metadata.create_all(engine)
