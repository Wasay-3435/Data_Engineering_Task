import sqlite3
from pathlib import Path


def connect(db_path: str | Path) -> sqlite3.Connection:
    """Open a SQLite connection with foreign-key enforcement enabled."""
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(
    connection: sqlite3.Connection,
    schema_path: str | Path,
) -> None:
    """Create the tables defined in the schema file."""
    schema_sql = Path(schema_path).read_text(encoding="utf-8")
    connection.executescript(schema_sql)
    connection.commit()
