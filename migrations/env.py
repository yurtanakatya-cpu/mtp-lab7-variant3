"""Настройки Alembic для каталога книг."""

from alembic import context

from lab7_app.database import database_url, open_engine
from lab7_app.models import Base

config = context.config
url = config.attributes.get("database_url") or database_url()


if context.is_offline_mode():
    context.configure(
        url=url,
        target_metadata=Base.metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    engine = open_engine(url)
    try:
        with engine.begin() as connection:
            context.configure(
                connection=connection,
                target_metadata=Base.metadata,
                render_as_batch=True,
            )
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()
