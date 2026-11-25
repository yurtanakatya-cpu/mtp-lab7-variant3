"""Консольные команды каталога."""

import argparse
import sys

from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .books import create_book, select_books
from .database import database_url, open_engine
from .schemas import BookInput


def build_parser() -> argparse.ArgumentParser:
    """Описать команды и аргументы."""
    parser = argparse.ArgumentParser(description="Каталог книг SQLite")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="вывести книги из таблицы")
    add = commands.add_parser("add", help="добавить книгу в каталог")
    add.add_argument("title", help="название")
    add.add_argument("author", help="автор")
    add.add_argument("--year", type=int, help="год издания")
    return parser


def run_command(args: argparse.Namespace, session: Session) -> int:
    """Выполнить команду с уже открытой сессией."""
    if args.command == "add":
        book = create_book(
            session,
            BookInput(title=args.title, author=args.author, year=args.year),
        )
        print(f"Добавлена книга с ID {book.id}.")
    elif args.command == "list":
        books = list(select_books(session))
        if not books:
            print("Каталог пуст.")
        for book in books:
            year = book.year if book.year is not None else "—"
            print(f"{book.id} | {book.title} | {book.author} | {year}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Запустить команду и вернуть код завершения."""
    args = build_parser().parse_args(argv)
    engine = open_engine(database_url())
    try:
        with Session(engine, expire_on_commit=False) as session:
            return run_command(args, session)
    except ValidationError as error:
        print(f"Некорректные данные: {error}", file=sys.stderr)
        return 1
    except SQLAlchemyError:
        print(
            "Ошибка работы с SQLite. Проверьте путь и примените миграции.",
            file=sys.stderr,
        )
        return 1
    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
