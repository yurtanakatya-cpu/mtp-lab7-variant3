"""Создать таблицу books."""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Создать начальную схему без поля года издания."""
    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("author", sa.String(100), nullable=False),
        sa.CheckConstraint(
            "length(trim(title)) BETWEEN 1 AND 120", name="ck_books_title"
        ),
        sa.CheckConstraint(
            "length(trim(author)) BETWEEN 1 AND 100", name="ck_books_author"
        ),
        sqlite_autoincrement=True,
    )


def downgrade() -> None:
    """Удалить таблицу при откате начальной миграции."""
    op.drop_table("books")
