"""ORM-модель, соответствующая последней версии схемы."""

from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс моделей каталога."""


class Book(Base):
    """Книга с названием, автором и необязательным годом издания."""

    __tablename__ = "books"
    __table_args__ = (
        CheckConstraint(
            "length(trim(title)) BETWEEN 1 AND 120", name="ck_books_title"
        ),
        CheckConstraint(
            "length(trim(author)) BETWEEN 1 AND 100", name="ck_books_author"
        ),
        CheckConstraint("year BETWEEN 1 AND 2100", name="ck_books_year"),
        {"sqlite_autoincrement": True},
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    author: Mapped[str] = mapped_column(String(100))
    year: Mapped[int | None]
