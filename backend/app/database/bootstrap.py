"""Database bootstrap and non-destructive compatibility migrations."""

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from app.database.connection import Base, get_engine


_COMPATIBILITY_COLUMNS = {
    "accounts": {
        "role": "VARCHAR(20) NOT NULL DEFAULT 'student'",
    },
    "users": {
        "email": "VARCHAR(100) NOT NULL DEFAULT ''",
        "phone": "VARCHAR(20) NOT NULL DEFAULT ''",
        "birth_date": "DATE",
        "target_city": "VARCHAR(50) NOT NULL DEFAULT ''",
        "target_salary": "VARCHAR(50) NOT NULL DEFAULT ''",
    },
    "user_competitions": {
        "competition_date": "DATE",
    },
    "job_applications": {
        "automation_status": "VARCHAR(40) NOT NULL DEFAULT 'idle'",
        # VARCHAR keeps this migration compatible with MySQL versions that
        # reject defaults on TEXT columns.
        "automation_error": "VARCHAR(2000) NOT NULL DEFAULT ''",
    },
    "recruitment_jobs": {
    },
}

_ADMIN_CONTROL_COLUMNS = {
    "accounts": {
        "management_version": "INTEGER NOT NULL DEFAULT 0",
    },
    "recruitment_jobs": {
        "moderation_status": "VARCHAR(20) NOT NULL DEFAULT 'allowed'",
        "management_version": "INTEGER NOT NULL DEFAULT 0",
    },
}


def ensure_compatibility_columns(engine: Engine, compatibility_columns=None) -> list[str]:
    """Add columns introduced after an existing database was initialized."""
    compatibility_columns = compatibility_columns or _COMPATIBILITY_COLUMNS
    table_names = set(inspect(engine).get_table_names())
    missing_columns: list[tuple[str, str, str]] = []
    for table_name, columns in compatibility_columns.items():
        if table_name not in table_names:
            continue
        existing_columns = {column["name"] for column in inspect(engine).get_columns(table_name)}
        missing_columns.extend(
            (table_name, name, definition)
            for name, definition in columns.items()
            if name not in existing_columns
        )

    if not missing_columns:
        return []

    with engine.begin() as connection:
        for table_name, name, definition in missing_columns:
            connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {name} {definition}"))
    return [f"{table_name}.{name}" for table_name, name, _ in missing_columns]


def ensure_sqlite_compatibility_columns(engine: Engine) -> list[str]:
    """Backward-compatible name retained for the existing migration tests."""
    return ensure_compatibility_columns(engine)


def initialize_database_schema(engine: Engine | None = None) -> list[str]:
    """Create missing tables and apply non-destructive SQLite compatibility changes."""
    # Import all ORM models before materializing SQLAlchemy metadata.
    import app.models  # noqa: F401

    active_engine = engine or get_engine()
    inspector = inspect(active_engine)
    if "business_admin_receipts" in inspector.get_table_names():
        columns = {column["name"] for column in inspector.get_columns("business_admin_receipts")}
        if "actor" in columns and "actor_id" not in columns:
            # Retain the provisional development schema without deleting records.
            with active_engine.begin() as connection:
                connection.execute(text("ALTER TABLE business_admin_receipts RENAME TO business_admin_receipts_legacy_v0"))
    Base.metadata.create_all(bind=active_engine)
    migrated = ensure_compatibility_columns(active_engine)
    # Keep the historical compatibility helper's return contract stable while
    # applying control-plane columns during normal application startup.
    admin_migrated = ensure_compatibility_columns(active_engine, _ADMIN_CONTROL_COLUMNS)
    return migrated + [item for item in admin_migrated if item not in migrated]
