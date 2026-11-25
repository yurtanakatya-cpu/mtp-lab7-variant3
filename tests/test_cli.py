"""CLI работает с мигрированной базой и CSV на диске."""

import csv
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from alembic import command

from lab7_app.database import PROJECT

from .support import migration_config


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        workspace = tempfile.TemporaryDirectory()
        self.addCleanup(workspace.cleanup)
        self.directory = Path(workspace.name)
        self.database = self.directory / "catalog.sqlite3"
        command.upgrade(migration_config(self.database), "head")

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "lab7_app", *args],
            cwd=PROJECT,
            env={
                **os.environ,
                "LAB7_DB_PATH": str(self.database),
                "PYTHONIOENCODING": "utf-8",
            },
            capture_output=True,
            encoding="utf-8",
            timeout=20,
        )

    def test_select_and_delete_use_persisted_data(self) -> None:
        added = self.run_cli("add", "Двенадцать стульев", "Ильф и Петров")
        self.assertEqual(added.returncode, 0, added.stderr)
        self.assertIn("1 | Двенадцать стульев", self.run_cli("list").stdout)
        missing = self.run_cli("delete", "99")
        self.assertEqual(missing.returncode, 1)
        self.assertIn("не найдена", missing.stderr)
        self.assertIn("Двенадцать стульев", self.run_cli("list").stdout)
        deleted = self.run_cli("delete", "1")
        self.assertEqual(deleted.returncode, 0, deleted.stderr)
        self.assertIn("Каталог пуст", self.run_cli("list").stdout)

    def test_export_preserves_quotes_and_refuses_to_overwrite(self) -> None:
        title = 'Повести, пьесы и "Очерки"'
        added = self.run_cli("add", title, "Автор")
        self.assertEqual(added.returncode, 0, added.stderr)
        csv_path = self.directory / "книги.csv"
        exported = self.run_cli("export", str(csv_path))
        self.assertEqual(exported.returncode, 0, exported.stderr)
        with csv_path.open(encoding="utf-8-sig", newline="") as stream:
            self.assertEqual(
                list(csv.reader(stream)),
                [["id", "title", "author", "year"], ["1", title, "Автор", ""]],
            )
        original = csv_path.read_bytes()
        self.assertEqual(self.run_cli("export", str(csv_path)).returncode, 1)
        self.assertEqual(csv_path.read_bytes(), original)
