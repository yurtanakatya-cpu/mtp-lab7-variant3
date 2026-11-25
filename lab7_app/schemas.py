"""Проверка данных книги до записи в SQLite."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

Title = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)
]
Author = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
]
Year = Annotated[int, Field(strict=True, ge=1, le=2100)]


class BookInput(BaseModel):
    """Данные для создания или полной замены книги."""

    model_config = ConfigDict(extra="forbid")

    title: Title
    author: Author
    year: Year | None = None


class BookRead(BookInput):
    """Представление ORM-записи в ответе FastAPI."""

    model_config = ConfigDict(from_attributes=True)
    id: int
