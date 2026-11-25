"""Операции каталога через SQLAlchemy."""

from collections.abc import Iterator

from sqlalchemy import delete, select, update
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


def get_book(session: Session, book_id: int) -> Book | None:
    """Найти книгу по первичному ключу."""
    return session.get(Book, book_id)


def replace_book(
    session: Session, book_id: int, data: BookInput
) -> Book | None:
    """Обновить все поля книги и вернуть результат записи."""
    query = (
        update(Book)
        .where(Book.id == book_id)
        .values(**data.model_dump())
        .returning(Book)
    )
    with session.begin():
        return session.scalar(query)


def delete_book(session: Session, book_id: int) -> bool:
    """Удалить книгу по ID и сообщить, была ли такая запись."""
    query = delete(Book).where(Book.id == book_id).returning(Book.id)
    with session.begin():
        return session.scalar(query) is not None
