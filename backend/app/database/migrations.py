from __future__ import annotations

from sqlalchemy import inspect, text

from app.database.session import engine


def run_startup_migrations() -> None:
    inspector = inspect(engine)
    if "devices" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("devices")}
    with engine.begin() as connection:
        if "connection_url" not in columns:
            connection.execute(text("ALTER TABLE devices ADD COLUMN connection_url TEXT"))
