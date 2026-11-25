"""Консольные команды каталога."""

import argparse
import sys
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .books import create_book, delete_book, select_books
from .csv_export import export_books
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
    delete = commands.add_parser("delete", help="удалить книгу по ID")
    delete.add_argument("book_id", type=positive_id, metavar="ID")
    export = commands.add_parser("export", help="выгрузить книги в CSV")
    export.add_argument("destination", type=Path, metavar="ФАЙЛ")
    return parser


def positive_id(value: str) -> int:
    """Проверить, что ID — положительное целое число."""
    try:
        book_id = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("ID должен быть целым") from error
    if not 1 <= book_id <= 2**63 - 1:
        raise argparse.ArgumentTypeError("ID вне диапазона SQLite")
    return book_id


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
    elif args.command == "delete":
        if not delete_book(session, args.book_id):
            print(f"Книга {args.book_id} не найдена.", file=sys.stderr)
            return 1
        print(f"Книга {args.book_id} удалена.")
    elif args.command == "export":
        count = export_books(session, args.destination)
        print(f"Записей выгружено: {count}. Файл: {args.destination}")
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
    except OSError as error:
        print(f"Не удалось записать CSV: {error}", file=sys.stderr)
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
