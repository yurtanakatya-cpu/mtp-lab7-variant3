"""Общие настройки SQLite для команд, API и миграций."""

from os import environ
from pathlib import Path

from sqlalchemy import URL, create_engine
from sqlalchemy.engine import Engine

PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE = PROJECT / "books.sqlite3"
SQLITE_MAX_ID = 2**63 - 1


def database_url(path: str | Path | None = None) -> URL:
    """Сформировать URL без ручного экранирования пути."""
    if path is None:
        path = environ.get("LAB7_DB_PATH", DEFAULT_DATABASE)
    resolved_path = Path(path).expanduser().resolve()
    return URL.create("sqlite", database=str(resolved_path))


def open_engine(url: URL) -> Engine:
    """Создать движок с транзакционным режимом sqlite3."""
    return create_engine(
        url, connect_args={"check_same_thread": False, "autocommit": False}
    )
