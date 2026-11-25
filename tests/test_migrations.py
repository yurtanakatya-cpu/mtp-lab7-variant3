"""Проверка переходов между ревизиями на SQLite с данными."""

import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from alembic import command

from .support import migration_config


class MigrationTests(unittest.TestCase):
    def test_upgrade_and_downgrade_preserve_existing_books(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "книги #100%.sqlite3"
            config = migration_config(path)
            command.upgrade(config, "0001")

            with closing(sqlite3.connect(path)) as connection:
                with connection:
                    connection.execute(
                        "INSERT INTO books (title, author) VALUES (?, ?)",
                        ("Капитанская дочка", "Александр Пушкин"),
                    )

            command.upgrade(config, "head")
            command.check(config)
            with closing(sqlite3.connect(path)) as connection:
                row = connection.execute(
                    "SELECT id, title, author, year FROM books"
                ).fetchone()
                self.assertEqual(
                    row, (1, "Капитанская дочка", "Александр Пушкин", None)
                )
                with self.assertRaises(sqlite3.IntegrityError), connection:
                    connection.execute("UPDATE books SET year = 2101")

            command.downgrade(config, "0001")
            with closing(sqlite3.connect(path)) as connection:
                fields = connection.execute("PRAGMA table_info(books)")
                self.assertEqual(
                    [field[1] for field in fields], ["id", "title", "author"]
                )
                rows = connection.execute("SELECT id, title FROM books")
                self.assertEqual(rows.fetchall(), [(1, "Капитанская дочка")])

            command.upgrade(config, "head")
            command.check(config)
