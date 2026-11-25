"""Выгрузка всей таблицы книг в новый CSV-файл."""

import csv
from pathlib import Path

from sqlalchemy.orm import Session

from .books import select_books


def export_books(session: Session, destination: Path) -> int:
    """Записать заголовок и строки книг, вернуть количество записей."""
    books = select_books(session)
    count = 0
    with destination.open("x", encoding="utf-8-sig", newline="") as target:
        writer = csv.writer(target)
        writer.writerow(("id", "title", "author", "year"))
        for book in books:
            writer.writerow((book.id, book.title, book.author, book.year))
            count += 1
    return count
