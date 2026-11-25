"""Временные базы для интеграционных тестов."""

from pathlib import Path

from alembic.config import Config

from lab7_app.database import PROJECT, database_url


def migration_config(db_path: Path) -> Config:
    """Собрать настройки Alembic с путём к конкретной тестовой БД."""
    config = Config(str(PROJECT / "alembic.ini"))
    config.attributes["database_url"] = database_url(db_path)
    return config
