"""Добавить необязательный год издания."""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Добавить поле year, оставив NULL у существующих книг."""
    op.add_column(
        "books",
        sa.Column(
            "year",
            sa.Integer(),
            sa.CheckConstraint(
                "year BETWEEN 1 AND 2100", name="ck_books_year"
            ),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Удалить поле year, сохранив названия, авторов и ID."""
    with op.batch_alter_table(
        "books", table_kwargs={"sqlite_autoincrement": True}
    ) as batch:
        batch.drop_constraint("ck_books_year", type_="check")
        batch.drop_column("year")
