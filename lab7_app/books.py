"""Операции каталога через SQLAlchemy."""

from collections.abc import Iterator

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Book
from .schemas import BookInput


def select_books(
    session: Session, *, offset: int = 0, limit: int | None = None
) -> Iterator[Book]:
    """Выбрать книги в порядке ID, при необходимости ограничить выдачу."""
    query = select(Book).order_by(Book.id).offset(offset).limit(limit)
    return iter(session.scalars(query))


def create_book(session: Session, data: BookInput) -> Book:
    """Сохранить новую книгу и получить её ID."""
    with session.begin():
        book = Book(**data.model_dump())
        session.add(book)
    return book
