"""REST API каталога, использующий сессии SQLAlchemy."""

from collections.abc import Iterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi import Path as PathParam
from sqlalchemy.orm import Session, sessionmaker

from .books import (
    create_book, delete_book, get_book, replace_book, select_books,
)
from .database import SQLITE_MAX_ID, database_url, open_engine
from .models import Book
from .schemas import BookInput, BookRead

BookId = Annotated[int, PathParam(ge=1, le=SQLITE_MAX_ID)]


def create_app(db_path: str | Path | None = None) -> FastAPI:
    """Создать API для выбранной SQLite, без изменения схемы базы."""
    engine = open_engine(database_url(db_path))
    sessions = sessionmaker(bind=engine, expire_on_commit=False)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        try:
            yield
        finally:
            engine.dispose()

    app = FastAPI(title="Каталог книг", version="1.0.0", lifespan=lifespan)

    def database_session() -> Iterator[Session]:
        """Предоставить отдельную сессию для каждого запроса."""
        with sessions() as session:
            yield session

    DbSession = Annotated[Session, Depends(database_session)]

    @app.get("/books", response_model=list[BookRead], summary="Выбрать книги")
    def list_books(
        session: DbSession,
        offset: Annotated[int, Query(ge=0, le=SQLITE_MAX_ID)] = 0,
        limit: Annotated[int, Query(ge=1, le=100)] = 50,
    ) -> list[Book]:
        return list(select_books(session, offset=offset, limit=limit))

    @app.post(
        "/books", response_model=BookRead, status_code=status.HTTP_201_CREATED,
        summary="Добавить книгу",
    )
    def add_book(
        data: BookInput, response: Response, session: DbSession
    ) -> Book:
        book = create_book(session, data)
        response.headers["Location"] = f"/books/{book.id}"
        return book

    @app.get(
        "/books/{book_id}", response_model=BookRead, summary="Найти книгу"
    )
    def read_book(book_id: BookId, session: DbSession) -> Book:
        book = get_book(session, book_id)
        if book is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Книга не найдена")
        return book

    @app.put(
        "/books/{book_id}", response_model=BookRead, summary="Заменить данные"
    )
    def update_book(
        book_id: BookId, data: BookInput, session: DbSession
    ) -> Book:
        book = replace_book(session, book_id, data)
        if book is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Книга не найдена")
        return book

    @app.delete(
        "/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT,
        summary="Удалить книгу",
    )
    def remove_book(book_id: BookId, session: DbSession) -> Response:
        if not delete_book(session, book_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Книга не найдена")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return app


app = create_app()
