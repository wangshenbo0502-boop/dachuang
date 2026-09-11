"""Database bootstrap and SQLite compatibility migrations."""

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from app.database.connection import Base, get_engine


_SQLITE_COMPATIBILITY_COLUMNS = {
    "users": {
        "email": "VARCHAR(100) NOT NULL DEFAULT ''",
        "phone": "VARCHAR(20) NOT NULL DEFAULT ''",
        "target_city": "VARCHAR(50) NOT NULL DEFAULT ''",
        "target_salary": "VARCHAR(50) NOT NULL DEFAULT ''",
    },
    "user_competitions": {
        "competition_date": "DATE",
    },
}


def ensure_sqlite_compatibility_columns(engine: Engine) -> list[str]:
    """Add known user-aggregate columns missing from legacy SQLite databases."""
    if engine.dialect.name != "sqlite":
        return []

    table_names = set(inspect(engine).get_table_names())
    missing_columns: list[tuple[str, str, str]] = []
    for table_name, columns in _SQLITE_COMPATIBILITY_COLUMNS.items():
        if table_name not in table_names:
            continue
        existing_columns = {column["name"] for column in inspect(engine).get_columns(table_name)}
        missing_columns.extend(
            (table_name, name, definition)
            for name, definition in columns.items()
            if name not in existing_columns
        )

    with engine.begin() as connection:
        for table_name, name, definition in missing_columns:
            connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {name} {definition}"))
    return [f"{table_name}.{name}" for table_name, name, _ in missing_columns]


def initialize_database_schema(engine: Engine | None = None) -> list[str]:
    """Create missing tables and apply non-destructive SQLite compatibility changes."""
    # Import all ORM models before materializing SQLAlchemy metadata.
    import app.models  # noqa: F401

    active_engine = engine or get_engine()
    Base.metadata.create_all(bind=active_engine)
    return ensure_sqlite_compatibility_columns(active_engine)
